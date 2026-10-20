import io
import os
import zipfile
from extractors.base import BaseExtractor


class ZipExtractor(BaseExtractor):
  """Распаковщик для ZIP-архивов."""

  def extract_from_file(self, source_path: str, target_dir: str) -> str:
    os.makedirs(target_dir, exist_ok=True)
    print(f"📦 Распаковка ZIP с диска: {source_path} -> {target_dir}")
    
    with zipfile.ZipFile(source_path, "r") as zf:
      zf.extractall(target_dir)
      extracted_files = zf.namelist()
      
    print(f"✅ Успешно распаковано файлов: {len(extracted_files)}")
    # Возвращаем путь к первому распакованному файлу (часто нужен для читалки)
    return os.path.join(target_dir, extracted_files[0]) if extracted_files else target_dir

  def extract_from_memory(self, source_buffer: io.BytesIO, target_dir: str, output_filename: str = None) -> str:
    os.makedirs(target_dir, exist_ok=True)
    print("📦 Распаковка ZIP из оперативной памяти (RAM)...")

    with zipfile.ZipFile(source_buffer, "r") as zf:
      zf.extractall(target_dir)
      extracted_files = zf.namelist()

    print(f"✅ Успешно распаковано из памяти файлов: {len(extracted_files)}")
    return os.path.join(target_dir, extracted_files[0]) if extracted_files else target_dir