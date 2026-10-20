"""Тесты для S3FileDownloader с использованием mock."""

import io
import pytest

from unittest.mock import MagicMock, patch
from downloader_pkg.s3_loader import S3FileDownloader


@patch("downloader_pkg.s3_loader.boto3.client")
def test_s3_downloader_anonymous_init(mock_boto_client):
  """Проверяем, что анонимный режим правильно настраивает сигнатуру."""
  downloader = S3FileDownloader(bucket_name="my-test-bucket", anonymous=True)
  assert downloader.bucket_name == "my-test-bucket"
  # Проверяем, что клиент boto3 был вызван с конфигурацией UNSIGNED
  mock_boto_client.assert_called_once()
  args, kwargs = mock_boto_client.call_args
  assert args[0] == "s3"
  assert "config" in kwargs


@patch("downloader_pkg.s3_loader.boto3.client")
def test_download_to_memory(mock_boto_client):
  """Проверяем скачивание файла в оперативную память (BytesIO)."""
  mock_s3_instance = MagicMock()
  mock_boto_client.return_value = mock_s3_instance

  downloader = S3FileDownloader(bucket_name="my-test-bucket")

  # Имитируем запись данных в поток при вызове download_fileobj
  def side_effect(bucket, key, fileobj):
    fileobj.write(b"header1,header2\nval1,val2")

  mock_s3_instance.download_fileobj.side_effect = side_effect

  buffer = downloader.download_to_memory("data/test.csv")

  assert isinstance(buffer, io.BytesIO)
  content = buffer.read().decode("utf-8")
  assert "header1,header2" in content