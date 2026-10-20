"""Модуль для скачивания файлов из S3-хранилищ (включая публичные бакеты без ключей)."""

import io
import os
import boto3
from botocore import UNSIGNED
from botocore.config import Config


class S3FileDownloader:
  """Загрузчик файлов из S3 с поддержкой анонимного доступа."""

  def __init__(self, bucket_name: str, anonymous: bool = True):
    self.bucket_name = bucket_name
    
    if anonymous:
      # Настройка для работы с публичными бакетами без AWS credentials
      self.s3_client = boto3.client(
          "s3", config=Config(signature_version=UNSIGNED)
      )
    else:
      # Стандартный клиент (будет искать ключи в env, файлах конфигурации и т.д.)
      self.s3_client = boto3.client("s3")

  def download_to_folder(self, s3_key: str, output_dir: str) -> str:
    """Режим 1: Скачивает файл из S3 в локальную папку."""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(s3_key)
    local_path = os.path.join(output_dir, filename)

    print(
        f"📥 Скачивание s3://{self.bucket_name}/{s3_key} в локальный файл:"
        f" {local_path}"
    )
    self.s3_client.download_file(self.bucket_name, s3_key, local_path)
    print("✅ Файл успешно сохранен на диск.")
    return local_path

  def download_to_memory(self, s3_key: str) -> io.BytesIO:
    """Режим 2: Загружает файл из S3 в оперативную память (BytesIO)

    без сохранения на жесткий диск.
    """
    print(
        f"📥 Загрузка s3://{self.bucket_name}/{s3_key} в оперативную память"
        " (RAM)..."
    )
    buffer = io.BytesIO()
    self.s3_client.download_fileobj(self.bucket_name, s3_key, buffer)
    # Возвращаем указатель в начало потока для последующего чтения
    buffer.seek(0)
    print("✅ Файл успешно загружен в оперативную память.")
    return buffer