import pytest
from downloader_pkg.base import BaseFileDownloader


class DummyDownloader(BaseFileDownloader):
    """Фейковый класс-наследник для тестирования абстрактного базового класса."""
    def _download_single(self, url: str):
        return url, "SUCCESS"
    def download_all(self):
        return {}


def test_url_validation():
    """Тест проверки валидности URL."""
    downloader = DummyDownloader(urls=[])
    
    # Валидные URL
    assert downloader._is_valid_url("https://example.com/file.zip") is True
    
    # Невалидные URL (пустые, с path traversal, некорректные типы)
    assert downloader._is_valid_url("") is False
    assert downloader._is_valid_url(None) is False
    assert downloader._is_valid_url("   ") is False
    assert downloader._is_valid_url("https://example.com/../secret.txt") is False


def test_get_filename():
    """Тест извлечения имени файла из URL."""
    downloader = DummyDownloader(urls=[])
    
    assert downloader._get_filename("https://example.com/folder/data.zip") == "data.zip"
    assert downloader._get_filename("https://example.com/file_name_only.tar.gz") == "file_name_only.tar.gz"
    # Если URL заканчивается на слэш, должен вернуться None
    assert downloader._get_filename("https://example.com/folder/") is None