import asyncio
import logging
import aiohttp
from .base import BaseFileDownloader

logger = logging.getLogger("AsyncFileDownloader")


class AsyncFileDownloader(BaseFileDownloader):
    """Асинхронный загрузчик на asyncio и aiohttp."""

    async def _download_single_async(self, session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
        """Асинхронный транспортный уровень."""
        cleaned_url = url.strip()
        
        if not self._is_valid_url(cleaned_url):
            return url, "INVALID_URL"

        filename = self._get_filename(cleaned_url)
        if not filename:
            return url, "FILE_NOT_FOUND"
            
        output_path = f"{self.output_dir}/{filename}"

        if self._check_already_exists(filename):
            return url, "ALREADY_EXISTS"

        try:
            logger.info("Асинхронный старт: %s", filename)
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with session.get(cleaned_url, timeout=timeout) as response:
                if response.status != 200:
                    return url, f"HTTP_ERROR_{response.status}"
                
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" in content_type:
                    return url, "INVALID_CONTENT_TYPE_HTML"

                content = await response.read()
                with open(output_path, "wb") as f:
                    f.write(content)
                    
            logger.info("Асинхронно сохранено: %s", filename)
            return url, "SUCCESS"

        except asyncio.TimeoutError:
            return url, "TIMEOUT"
        except aiohttp.ClientError:
            return url, "CONNECTION_ERROR"
        except Exception as e:
            return url, f"ERROR_{type(e).__name__}"

    def _download_single(self, url: str) -> tuple[str, str]:
        """Заглушка, так как мы переопределяем download_all для асинхронности."""
        pass

    async def download_all_async(self) -> dict[str, str]:
        """Асинхронная оркестрация через asyncio.gather."""
        logger.info("Старт пакетной асинхронной загрузки %s файлов.", len(self.urls))
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_single_async(session, url) for url in self.urls]
            results = await asyncio.gather(*tasks)
        logger.info("Асинхронная загрузка завершена.")
        return dict(results)

    def download_all(self) -> dict[str, str]:
        """Синхронная точка входа для запуска async-кода из основного потока."""
        return asyncio.run(self.download_all_async())