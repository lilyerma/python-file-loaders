import logging
import os
import wget
from .base import BaseFileDownloader

logger = logging.getLogger("WgetFileDownloader")


class WgetFileDownloader(BaseFileDownloader):
    """Загрузчик, использующий стороннюю библиотеку wget."""

    def _fetch(self, cleaned_url: str, output_path: str, filename: str) -> str:
        try:
            wget.download(cleaned_url, out=output_path)
            return "SUCCESS"
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise ConnectionError(f"Wget error: {e}")

    def _download_single(self, url: str) -> tuple[str, str]:
        return self._safe_download_wrapper(url)

    def download_all(self) -> dict[str, str]:
        """Последовательная загрузка через wget."""
        results = {}
        for url in self.urls:
            _, status = self._download_single(url)
            results[url] = status
        return results