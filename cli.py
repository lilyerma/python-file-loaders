import os
import shutil
import logging
import argparse
from downloader_pkg import (
    ThreadFileDownloader,
    AsyncFileDownloader,
    RequestsFileDownloader,
    WgetFileDownloader
)
from extractor import ZipExtractor
from benchmark import run_benchmark

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CLI")

RAW_DIR = "divvy_zips"
EXTRACTED_DIR = "divvy_extracted"
BENCH_DIRS = ["bench_requests", "bench_thread", "bench_wget", "bench_async"]

# Дефолтный список ссылок на случай, если пользователь не передал свои
DEFAULT_URIS = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q3.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2020_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip",
]

# Словарь-фабрика для выбора нужного класса по строковому ключу
LOADER_CLASSES = {
    "thread": ThreadFileDownloader,
    "async": AsyncFileDownloader,
    "requests": RequestsFileDownloader,
    "wget": WgetFileDownloader,
}


def cmd_download(args):
    """Команда скачивания с выбором метода и списка файлов."""
    # Если пользователь передал свои ссылки через аргументы, используем их, иначе дефолтные
    urls_to_download = args.urls if args.urls else DEFAULT_URIS
    
    method = args.method.lower()
    if method not in LOADER_CLASSES:
        logger.error("Неизвестный метод загрузки: '%s'. Выберите из: %s", method, list(LOADER_CLASSES.keys()))
        return

    logger.info("Запуск скачивания. Метод: [%s], Файлов: %s, Папка: %s", method, len(urls_to_download), RAW_DIR)

    # Получаем нужный класс из словаря
    loader_class = LOADER_CLASSES[method]

    # Инициализируем загрузчик (для thread передаем max_workers, для остальных — нет)
    if method == "thread":
        downloader = loader_class(urls=urls_to_download, output_dir=RAW_DIR, max_workers=args.workers)
    else:
        downloader = loader_class(urls=urls_to_download, output_dir=RAW_DIR)

    # Запускаем загрузку
    report = downloader.download_all()
    logger.info("Скачивание завершено. Отчёт: %s", report)


def cmd_extract(args):
    """Команда распаковки архивов."""
    logger.info("Запуск распаковки из %s в %s", RAW_DIR, EXTRACTED_DIR)
    extractor = ZipExtractor(source_dir=RAW_DIR, target_dir=EXTRACTED_DIR)
    extractor.extract_and_clean_all()
    logger.info("Распаковка и очистка архивов завершена.")


def cmd_clean(args):
    """Команда удаления всех созданных папок."""
    logger.info("Очистка всех временных данных...")
    dirs_to_clean = [RAW_DIR, EXTRACTED_DIR] + BENCH_DIRS
    
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                logger.info("Удалена папка: %s", d)
            except Exception as e:
                logger.error("Не удалось удалить папку %s: %s", d, e)
        else:
            logger.info("Папка не найдена (пропуск): %s", d)
            
    logger.info("Очистка успешно завершена!")


def main():
    parser = argparse.ArgumentParser(
        description="🚀 CLI-менеджер для скачивания, распаковки и управления архивами.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды для выполнения")

    # --- 1. Команда: download ---
    parser_download = subparsers.add_parser(
        "download", 
        help="Скачать zip-архивы по URL-адресам",
        description="Загружает файлы, используя выбранный сетевой метод."
    )
    parser_download.add_argument(
        "-m", "--method", 
        type=str, 
        default="thread", 
        choices=list(LOADER_CLASSES.keys()), 
        help="Способ скачивания:\n"
             "  - thread   (многопоточный через ThreadPoolExecutor, по умолчанию)\n"
             "  - async    (асинхронный через asyncio + aiohttp)\n"
             "  - requests (последовательный через requests)\n"
             "  - wget     (последовательный через wget с прогресс-баром)"
    )
    parser_download.add_argument(
        "-w", "--workers", 
        type=int, 
        default=3, 
        help="Количество одновременных потоков (только для метода 'thread', default: 3)"
    )
    parser_download.add_argument(
        "urls", 
        nargs="*", 
        help="(Необязательно) Список URL через пробел. Если не указаны, скачиваются дефолтные архивы Divvy."
    )

    # --- 2. Команда: extract ---
    subparsers.add_parser(
        "extract", 
        help="Распаковать скачанные архивы",
        description="Находит все .zip архивы в папке загрузок, распаковывает их и удаляет оригиналы."
    )

    # --- 3. Команда: clean ---
    subparsers.add_parser(
        "clean", 
        help="Удалить все созданные папки и файлы",
        description="Стирает папки с архивами, распакованными данными и мусором от бенчмарков."
    )

    # --- 4. Команда: benchmark ---
    subparsers.add_parser(
        "benchmark", 
        help="Запустить сравнение скорости всех загрузчиков",
        description="Замеряет и сравнивает время работы thread, async, requests и wget."
    )

    args = parser.parse_args()

    # Маршрутизатор
    if args.command == "download":
        cmd_download(args)
    elif args.command == "extract":
        cmd_extract(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "benchmark":
        logger.info("Запуск бенчмарка производительности...")
        run_benchmark()
    else:
        # Если команда не передана или введена с ошибкой, выводим справку
        parser.print_help()


if __name__ == "__main__":
    main()