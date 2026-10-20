import time
import logging
from downloader_pkg import (
    ThreadFileDownloader,
    RequestsFileDownloader,
    WgetFileDownloader,
    AsyncFileDownloader
)


# Настройка логирования (включим уровень INFO, чтобы видеть процесс)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Benchmark")

# Для теста возьмем список ссылок 
# (для быстроты бенчмарка можно оставить 2-3 файла, чтобы не ждать гигабайты)
benchmark_uris = [
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q1.zip",
    "https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2019_Q2.zip",
]


def run_benchmark():
    # Список загрузчиков для теста: (Имя, Класс, Аргументы инициализации)
    loaders = [
        ("Синхронный (Requests)", RequestsFileDownloader, {"output_dir": "bench_requests"}),
        ("Потоковый (ThreadPool, 3 воркера)", ThreadFileDownloader, {"output_dir": "bench_thread", "max_workers": 3}),
        ("Синхронный (Wget)", WgetFileDownloader, {"output_dir": "bench_wget"}),
        ("Асинхронный (Asyncio + aiohttp)", AsyncFileDownloader, {"output_dir": "bench_async"})
    ]

    results = {}

    logger.info("=== СТАРТ ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ ===")
    logger.info("Тестовых файлов в списке: %s\n", len(benchmark_uris))

    for name, loader_class, kwargs in loaders:
        logger.info("--- Запуск теста для: %s ---", name)
        
        # Создаем экземпляр загрузчика
        downloader = loader_class(urls=benchmark_uris, **kwargs)
        
        # Замеряем время выполнения
        start_time = time.perf_counter()
        
        try:
            report = downloader.download_all()
            end_time = time.perf_counter()
            
            elapsed_time = end_time - start_time
            results[name] = elapsed_time
            logger.info("✓ %s завершил работу за %.2f секунды\n", name, elapsed_time)
            
        except Exception as e:
            logger.error("❌ Ошибка при выполнении %s: %s\n", name, e)
            results[name] = None

    # --- ИТОГОВАЯ СВОДКА ---
    logger.info("=" * 50)
    logger.info(" РЕЗУЛЬТАТЫ СРАВНЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ:")
    logger.info("=" * 50)
    
    # Сортируем результаты по времени (от самых быстрых к медленным)
    sorted_results = sorted(
        {k: v for k, v in results.items() if v is not None}.items(), 
        key=lambda item: item[1]
    )

    for rank, (name, duration) in enumerate(sorted_results, 1):
        logger.info("%s. %-35s : %.2f сек.", rank, name, duration)
        
    logger.info("=" * 50)


if __name__ == "__main__":
    run_benchmark()