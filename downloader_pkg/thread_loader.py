import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseFileDownloader

logger = logging.getLogger("ThreadFileDownloader")


class ThreadFileDownloader(BaseFileDownloader):
    """Потоковый загрузчик, использующий общую базовую логику."""

    def __init__(self, urls: list[str], output_dir: str = "downloads", max_workers: int = 4):
        super().__init__(urls, output_dir)
        self.max_workers = max_workers

    def _fetch(self, cleaned_url: str, output_path: str, filename: str) -> str:
        """Реализация транспорта с HEAD и GET запросами для потоков."""
        # HEAD-запрос для проверки размера
        head_response = requests.head(cleaned_url, timeout=10, allow_redirects=True)
        if head_response.status_code == 200:
            size = head_response.headers.get("Content-Length")
            if size:
                logger.info("Размер '%s': %.2f MB", filename, int(size) / (1024 * 1024))

        # GET-запрос с потоковой передачей
        response = requests.get(cleaned_url, timeout=30, stream=True)
        
        if response.status_code != 200:
            raise ConnectionError(f"HTTP Error {response.status_code}")
        
        if "text/html" in response.headers.get("Content-Type", "").lower():
            return "INVALID_CONTENT_TYPE_HTML"

        # Запись на диск чанками
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        return "SUCCESS"

    def _download_single(self, url: str) -> tuple[str, str]:
        return self._safe_download_wrapper(url)

    def download_all(self) -> dict[str, str]:
        """Оркестрация через ThreadPoolExecutor."""
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self._download_single, url): url for url in self.urls}
            for future in as_completed(future_to_url):
                url, status = future.result()
                results[url] = status
        return results