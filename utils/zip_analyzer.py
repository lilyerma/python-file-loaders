import os
import logging
from pathlib import Path
from extractors.zip_extractor import ZipExtractor
from utils.csv_analyzer import CsvAnalyzer

logger = logging.getLogger("ZipAnalyzer")

class ZipAnalyzer:
    """Распаковывает один или все ZIP-архивы в папке и анализирует CSV без сохранения DDL."""

    def __init__(self, target_path: str | Path, temp_dir: str | Path = "./temp_extracted"):
        self.target_path = Path(target_path)
        self.temp_dir = Path(temp_dir)

        if not self.target_path.exists():
            logger.error("❌ Указанный путь не существует: %s", self.target_path)
            self.zip_files = []
            return

        # Собираем список файлов для обработки
        if self.target_path.is_dir():
            self.zip_files = list(self.target_path.glob("*.zip"))
            logger.info("📁 Обнаружена папка. Найдено ZIP-архивов для анализа: %d", len(self.zip_files))
        else:
            self.zip_files = [self.target_path]

        if not self.zip_files:
            logger.warning("❌ В указанном пути не найдено ZIP-файлов: %s", self.target_path)

    def run(self):
        """Запускает процесс распаковки и анализа для всех найденных архивов."""
        if not self.zip_files:
            return

        extractor = ZipExtractor()

        for zip_path in self.zip_files:
            logger.info("\n" + "="*50)
            logger.info("📦 Обработка архива: %s", zip_path)
            logger.info("="*50)
            
            try:
                # Создаем уникальную подпапку для каждого архива через pathlib
                sub_target_dir = self.temp_dir / zip_path.stem
                
                # Распаковываем через ZipExtractor
                extractor.extract_from_file(str(zip_path), str(sub_target_dir))

                logger.info("📊 Запуск CSV-анализатора...")
                # Запускаем анализ распакованных данных
                analyzer = CsvAnalyzer(
                    root_dir=sub_target_dir,
                    ddl_output_dir=None 
                )
                analyzer.run_analysis()

            except Exception as e:
                logger.error("❌ Ошибка при анализе архива %s: %s", zip_path, e, exc_info=True)