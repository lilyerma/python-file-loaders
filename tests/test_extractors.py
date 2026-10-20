"""Тесты для распаковщиков ZIP и GZ."""

import gzip
import io
import os
import zipfile
import pytest
from extractors.gz_extractor import GzipExtractor
from extractors.zip_extractor import ZipExtractor


def test_zip_extractor_from_memory(tmp_path):
  """Тест распаковки ZIP-архива из оперативной памяти."""
  # Создаем ZIP-архив в памяти
  zip_buffer = io.BytesIO()
  with zipfile.ZipFile(zip_buffer, "w") as zf:
    zf.writestr("test_file.csv", "id,name\n1,test")
  zip_buffer.seek(0)

  extractor = ZipExtractor()
  target_dir = tmp_path / "extracted"
  
  result_path = extractor.extract_from_memory(zip_buffer, str(target_dir))

  assert os.path.exists(result_path)
  with open(result_path, "r", encoding="utf-8") as f:
    content = f.read()
    assert "id,name" in content


def test_gzip_extractor_from_memory(tmp_path):
  """Тест распаковки GZ-файла из оперативной памяти."""
  # Создаем GZ данные в памяти
  gz_buffer = io.BytesIO()
  with gzip.GzipFile(fileobj=gz_buffer, mode="wb") as gz:
    gz.write(b"col1,col2\n100,200")
  gz_buffer.seek(0)

  extractor = GzipExtractor()
  target_dir = tmp_path / "extracted_gz"

  result_path = extractor.extract_from_memory(
      gz_buffer, str(target_dir), output_filename="data.csv"
  )

  assert os.path.exists(result_path)
  with open(result_path, "r", encoding="utf-8") as f:
    content = f.read()
    assert "col1,col2" in content