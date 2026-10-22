from abc import ABC, abstractmethod
import os
import logging

logger = logging.getLogger("BaseDownloader")


class BaseFileDownloader(ABC):
    """Абстрактный базовый класс с общей логикой валидации и обработки ошибок."""
    
    def __init__(self, urls: list[str], output_dir: str = "downloads"):
        self.urls = urls
        self.output_dir = output_dir.rstrip("/")
        os.makedirs(self.output_dir, exist_ok=True)

    def _is_valid_url(self, url: str) -> bool:
        """1. Валидация URL."""
        if not url or not isinstance(url, str):
            return False
        cleaned = url.strip()
        if not cleaned or ".." in cleaned:
            return False
        return True

    def _get_filename(self, url: str) -> str | None:
        """2. Извлечение имени файла."""
        parts = url.split("/")
        return parts[-1] if parts and parts[-1] else None

    def _check_already_exists(self, filename: str) -> bool:
        """3. Проверка, существует ли файл."""
        output_path = os.path.join(self.output_dir, filename)
        return os.path.exists(output_path)

    def _prepare(self, url: str) -> tuple[str | None, str | None, str | None, str | None]:
        """
        Общая логика подготовки: валидация, имя, путь и проверка существования.
        Возвращает кортеж (cleaned_url, filename, output_path, status_or_skip).
        Если status_or_skip не None, значит файл нужно пропустить с этим статусом.
        """
        cleaned_url = url.strip()
        
        if not self._is_valid_url(cleaned_url):
            logger.warning("Пропущено (невалидный URL): '%s'", url)
            return cleaned_url, None, None, "INVALID_URL"

        filename = self._get_filename(cleaned_url)
        if not filename:
            logger.warning("Не удалось определить имя файла для URL: '%s'", cleaned_url)
            return cleaned_url, None, None, "FILE_NOT_FOUND"
            
        output_path = os.path.join(self.output_dir, filename)

        if self._check_already_exists(filename):
            logger.info("Файл уже существует, пропуск: %s", filename)
            return cleaned_url, filename, output_path, "ALREADY_EXISTS"

        return cleaned_url, filename, output_path, None

    def _safe_download_wrapper(self, url: str) -> tuple[str, str]:
        """
        Шаблонный метод (Template Method) для синхронных загрузчиков.
        """
        cleaned_url, filename, output_path, skip_status = self._prepare(url)
        if skip_status:
            return url, skip_status

        try:
            logger.info("Старт загрузки: %s", filename)
            status = self._fetch(cleaned_url, output_path, filename)
            logger.info("Успешно обработано: %s", filename)
            return url, status

        except TimeoutError:
            logger.warning("Таймаут для '%s'", filename)
            return url, "TIMEOUT"
        except ConnectionError:
            logger.error("Ошибка сети для '%s'", filename)
            return url, "CONNECTION_ERROR"
        except Exception as e:
            logger.exception("Непредвиденная ошибка для '%s': %s", filename, e)
            return url, f"ERROR_{type(e).__name__}"

    @abstractmethod
    def _fetch(self, cleaned_url: str, output_path: str, filename: str) -> str:
        """Абстрактный метод транспорта для реализации конкретным загрузчиком."""
        pass

    @abstractmethod
    def download_all(self) -> dict[str, str]:
        """Оркестрация загрузки."""
        pass

