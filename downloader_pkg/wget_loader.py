import logging
import os
import wget
from .base import BaseFileDownloader

logger = logging.getLogger("WgetFileDownloader")


class WgetFileDownloader(BaseFileDownloader):
    """Загрузчик, использующий стороннюю библиотеку wget."""

    def _download_single(self, url: str) -> tuple[str, str]:
        def transport_logic(cleaned_url, output_path, filename):
            # wget скачивает файл напрямую по указанному пути назначения
            try:
                wget.download(cleaned_url, out=output_path)
                return "SUCCESS"
            except Exception as e:
                # Если файл успел частично создаться при ошибке, удалим его
                if os.path.exists(output_path):
                    os.remove(output_path)
                raise ConnectionError(f"Wget error: {e}")

        return self._safe_download_wrapper(url, transport_logic)

    def download_all(self) -> dict[str, str]:
        """Последовательная загрузка через wget."""
        results = {}
        for url in self.urls:
            _, status = self._download_single(url)
            results[url] = status
        return results