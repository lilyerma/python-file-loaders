import os
import shutil
import logging
import argparse
from csv_to_pg_loader.sql_runner import SqlScriptRunner
from downloader_pkg import (
    ThreadFileDownloader,
    AsyncFileDownloader,
    RequestsFileDownloader,
    WgetFileDownloader
)
from extractors.zip_extractor import ZipExtractor
from benchmark import run_benchmark
from noaa_loader import NoaaPipeline
from experiment_s3 import run_experiment
from json_flattening.converter_json_csv import RaggedJsonToCsvConverter
from csv_to_pg_loader.analyzer import CsvAnalyzer
from csv_to_pg_loader.sql_saver import SqlScriptSaver
from csv_to_pg_loader.db_manager import DatabaseManager
from csv_to_pg_loader.sql_runner import SqlScriptRunner

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
NOAA_DIR = "downloads"
CSV_RESULT = "output_csv"

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
    dirs_to_clean = [RAW_DIR, EXTRACTED_DIR, NOAA_DIR, CSV_RESULT] + BENCH_DIRS
    
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


def handle_noaa_command(args):
  try:
    client = NoaaPipeline(base_url=args.url, output_dir=args.output_dir)
    client.run_pipeline(target_timestamp=args.timestamp)
  except Exception as e:
    print(f"❌ Ошибка выполнения NOAA пайплайна: {e}")

def cmd_experiment(args):
  """Команда для запуска S3-эксперимента по CommonCrawl."""
  print("🚀 Запуск S3-эксперимента из CLI...")
  try:
    run_experiment()
    print("✨ Эксперимент успешно завершен!")
  except Exception as e:
    print(f"❌ Ошибка во время выполнения эксперимента: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="🚀 CLI-менеджер для запуска шагов и упражнений по работе с файлами.",
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

    # --- 5. Команда: noaa ---
    parser_noaa = subparsers.add_parser(
        "noaa",
        help=(
          "Поиск по таймстампу, скачивание и обработка климатического файла с"
          " NOAA"
        ),
    )
    parser_noaa.add_argument(
        "--url",
        default=NoaaPipeline.DEFAULT_URL,
        help="Базовый URL каталога NOAA NCEI",
    )
    parser_noaa.add_argument(
        "--timestamp",
        required=True,
        help='Таймстамп для поиска в таблице, например: "2024-01-19 15:42"',
    )
    parser_noaa.add_argument(
        "--output-dir",
        default="./downloads",
        help="Директория для сохранения скачанного файла",
    )

    # ПАРСЕР: experiment c s3 (на самом деле с открытым хранилищем)
    parser_experiment = subparsers.add_parser(
      "experiment",
      help="Запустить эксперимент с CommonCrawl, стримингом и памятью",
    )

    # ПАРСЕР: поиск JSON-файлов по директории с разной глубиной и уплощение в csv
    convert_parser = subparsers.add_parser(
      "convert",
      help="Рекурсивный поиск JSON-файлов, флаттенинг вложенных структур и конвертация в CSV",
    )
    convert_parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="./data",
        help="Директория с исходными JSON-файлами (по умолчанию: ./data)",
    )
    convert_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./output_csv",
        help=(
            "Директория для сохранения плоских CSV-файлов (по умолчанию:"
            " ./output_csv)"
        ),
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Найти CSV файлы в папке и вывести отчет по типам, min/max и null значениям",
    )
    analyze_parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="csv_to_pg_loader/data",
        help="Путь к директории с CSV файлами",
    )

    # --- Команда: run-sql ---
    run_parser = subparsers.add_parser(
        "run-sql",
        help="Запустить все сохраненные .sql скрипты в PostgreSQL",
    )
    run_parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default="csv_to_pg_loader/sql",
        help="Путь к директории с .sql файлами",
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
    elif args.command == "noaa":
      print("🚀 Запуск NOAA пайплайна...")
      try:
          pipeline = NoaaPipeline(base_url=args.url, output_dir=args.output_dir)
          pipeline.run(target_timestamp=args.timestamp)
          print("✨ Задача по NOAA успешно выполнена!")
      except Exception as e:
          print(f"❌ Ошибка: {e}")
    elif args.command == "experiment":
        cmd_experiment(args)
    elif args.command == "convert":
        print(
            f"Запуск конвертации из '{args.input}' в целевую папку '{args.output}'..."
        )
        converter = RaggedJsonToCsvConverter(
            root_dir=args.input, output_dir=args.output
        )
        converted_files = converter.process_all()
        print(f"Готово! Успешно конвертировано файлов: {len(converted_files)}")
    elif args.command == "analyze":
        print(f"📊 Запуск анализа данных по пути: {args.input}")
        analyzer = CsvAnalyzer(root_dir=args.input)
        analyzer.run_analysis()
    elif args.command == "save-sql":
        saver = SqlScriptSaver()
        saved_path = saver.save(filename=args.name, script_content=args.content)

        print(f"✨ Готово! SQL-скрипт успешно сохранен: {saved_path}")

    elif args.command == "run-sql":
        # Инициализируем менеджер БД и раннер скриптов
        db_manager = DatabaseManager()
        runner = SqlScriptRunner(db_manager=db_manager)

        # Запускаем выполнение папки
        runner.run_folder(args.dir)
    else:
        # Если команда не передана или введена с ошибкой, выводим справку
        parser.print_help()


if __name__ == "__main__":
    main()