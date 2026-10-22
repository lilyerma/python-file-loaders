# factory.py
from typing import List
from .base import BaseFileDownloader
from .requests_loader import RequestsFileDownloader
from .thread_loader import ThreadFileDownloader
from .wget_loader import WgetFileDownloader
from .async_loader import AsyncFileDownloader
from .s3_loader import S3FileDownloader


class DownloaderFactory:
    """Фабрика для создания экземпляров загрузчиков по типу."""

    @staticmethod
    def create_downloader(
        loader_type: str, 
        urls: List[str] = None, 
        output_dir: str = "downloads", 
        **kwargs
    ) -> BaseFileDownloader | S3FileDownloader:
        """
        Создает и возвращает нужный загрузчик на основе переданной строки.
        """
        loader_type = loader_type.lower().strip()

        if loader_type == "requests":
            return RequestsFileDownloader(urls=urls, output_dir=output_dir)
        
        elif loader_type == "thread":
            max_workers = kwargs.get("max_workers", 4)
            return ThreadFileDownloader(urls=urls, output_dir=output_dir, max_workers=max_workers)
        
        elif loader_type == "wget":
            return WgetFileDownloader(urls=urls, output_dir=output_dir)
        
        elif loader_type == "async":
            return AsyncFileDownloader(urls=urls, output_dir=output_dir)
        
        elif loader_type == "s3":
            # Для S3 специфичные аргументы (bucket_name и s3_key/фолдер)
            bucket_name = kwargs.get("bucket_name")
            if not bucket_name:
                raise ValueError("Для S3 загрузчика обязательно требуется параметр bucket_name")
            anonymous = kwargs.get("anonymous", True)
            return S3FileDownloader(bucket_name=bucket_name, anonymous=anonymous)
        
        else:
            raise ValueError(
                f"Неизвестный тип загрузчика: '{loader_type}'. "
                f"Доступные варианты: requests, thread, wget, async, s3"
            )