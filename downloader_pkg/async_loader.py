import asyncio
import logging
import aiohttp
from .base import BaseFileDownloader

logger = logging.getLogger("AsyncFileDownloader")


class AsyncFileDownloader(BaseFileDownloader):
    """Асинхронный загрузчик на asyncio и aiohttp."""

    async def _download_single_async(self, session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
        """Асинхронный транспортный уровень с использованием базовой подготовки."""
        cleaned_url, filename, output_path, skip_status = self._prepare(url)
        if skip_status:
            return url, skip_status

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

    def _fetch(self, cleaned_url: str, output_path: str, filename: str) -> str:
        """Заглушка для соблюдения контракта базового класса."""
        pass

    def _download_single(self, url: str) -> tuple[str, str]:
        """Заглушка для синхронного интерфейса."""
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