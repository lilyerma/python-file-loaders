import io
import os
import logging
import boto3
from botocore import UNSIGNED
from botocore.config import Config

logger = logging.getLogger("S3FileDownloader")


class S3FileDownloader:
    """Загрузчик файлов из S3 с поддержкой анонимного доступа."""

    def __init__(self, bucket_name: str, anonymous: bool = True):
        self.bucket_name = bucket_name
        
        if anonymous:
            self.s3_client = boto3.client(
                "s3", config=Config(signature_version=UNSIGNED)
            )
        else:
            self.s3_client = boto3.client("s3")

    def download_to_folder(self, s3_key: str, output_dir: str) -> str:
        """Режим 1: Скачивает файл из S3 в локальную папку."""
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(s3_key)
        local_path = os.path.join(output_dir, filename)

        logger.info("Скачивание s3://%s/%s в локальный файл: %s", self.bucket_name, s3_key, local_path)
        self.s3_client.download_file(self.bucket_name, s3_key, local_path)
        logger.info("Файл успешно сохранен на диск.")
        return local_path

    def download_to_memory(self, s3_key: str) -> io.BytesIO:
        """Режим 2: Загружает файл из S3 в оперативную память (BytesIO)."""
        logger.info("Загрузка s3://%s/%s в оперативную память (RAM)...", self.bucket_name, s3_key)
        buffer = io.BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, s3_key, buffer)
        buffer.seek(0)
        logger.info("Файл успешно загружен в оперативную память.")
        return buffer