import os
import zipfile
import logging

logger = logging.getLogger("ZipExtractor")


class ZipExtractor:
    """Класс для распаковки ZIP-архивов из исходной папки в целевую с удалением оригиналов."""
    
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = source_dir.rstrip("/")
        self.target_dir = target_dir.rstrip("/")
        
        # Автоматически создаем целевую папку, если её нет
        os.makedirs(self.target_dir, exist_ok=True)
        logger.info("Инициализирован распаковщик. Источник: %s -> Назначение: %s", self.source_dir, self.target_dir)

    def extract_and_clean_all(self) -> dict[str, str]:
        """Находит все .zip файлы в source_dir, распаковывает в target_dir и удаляет исходники."""
        results = {}
        
        if not os.path.exists(self.source_dir):
            logger.warning("Исходная папка не найдена: %s", self.source_dir)
            return results

        # Перебираем все файлы в исходной папке
        for filename in os.listdir(self.source_dir):
            if filename.endswith(".zip"):
                zip_path = os.path.join(self.source_dir, filename)
                logger.info("Обнаружен архив для распаковки: %s", filename)

                try:
                    # Открываем и распаковываем в целевую папку
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.target_dir)
                    
                    logger.info("Успешно распаковано в %s: %s", self.target_dir, filename)
                    results[filename] = "EXTRACTED"

                    # Удаляем исходный ZIP-файл после успешной распаковки
                    os.remove(zip_path)
                    logger.info("Исходный архив удален: %s", filename)

                except zipfile.BadZipFile:
                    logger.error("Ошибка: файл %s поврежден или не является zip-архивом.", filename)
                    results[filename] = "BAD_ZIP_FILE"
                except Exception as e:
                    logger.exception("Непредвиденная ошибка при обработке архива %s: %s", filename, e)
                    results[filename] = f"ERROR_{type(e).__name__}"

        logger.info("Распаковка всех архивов завершена.")
        return results