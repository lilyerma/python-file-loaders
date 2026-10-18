import logging
import requests
from .base import BaseFileDownloader

logger = logging.getLogger("RequestsFileDownloader")


class RequestsFileDownloader(BaseFileDownloader):
    """Простой синхронный последовательный загрузчик на requests."""

    def _download_single(self, url: str) -> tuple[str, str]:
        def transport_logic(cleaned_url, output_path, filename):
            response = requests.get(cleaned_url, timeout=30, stream=True)
            
            if response.status_code != 200:
                raise ConnectionError(f"HTTP Error {response.status_code}")
            
            if "text/html" in response.headers.get("Content-Type", "").lower():
                return "INVALID_CONTENT_TYPE_HTML"

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return "SUCCESS"

        return self._safe_download_wrapper(url, transport_logic)

    def download_all(self) -> dict[str, str]:
        """Последовательный обход списка файлов."""
        results = {}
        for url in self.urls:
            _, status = self._download_single(url)
            results[url] = status
        return results