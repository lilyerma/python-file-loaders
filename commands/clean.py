import os
import shutil
import logging

logger = logging.getLogger("CLI.Clean")
DEFAULT_RAW_DIR = "divvy_zips"
DEFAULT_EXTRACTED_DIR = "divvy_extracted"
DEFAULT_NOAA_DIR = "downloads"
DEFAULT_CSV_RESULT = "output_csv"
DEFAULT_BENCH_DIRS = ["bench_requests", "bench_thread", "bench_wget", "bench_async"]

def run(args):
    """Очистка всех временных директорий."""
    logger.info("Очистка всех временных данных...")
    dirs_to_clean = [DEFAULT_RAW_DIR, DEFAULT_EXTRACTED_DIR, DEFAULT_NOAA_DIR, DEFAULT_CSV_RESULT] + DEFAULT_BENCH_DIRS
    
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