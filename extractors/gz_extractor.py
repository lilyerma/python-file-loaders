import gzip
import io
import os
from extractors.base import BaseExtractor


class GzipExtractor(BaseExtractor):
  """Распаковщик для GZ-архивов."""

  def extract_from_file(self, source_path: str, target_dir: str) -> str:
    os.makedirs(target_dir, exist_ok=True)
    # Убираем расширение .gz, чтобы получить имя итогового файла (например, data.csv)
    base_name = os.path.basename(source_path)
    target_filename = base_name[:-3] if base_name.endswith(".gz") else base_name + ".unpacked"
    target_path = os.path.join(target_dir, target_filename)

    print(f"📦 Распаковка GZ с диска: {source_path} -> {target_path}")
    
    with gzip.open(source_path, "rb") as f_in, open(target_path, "wb") as f_out:
      f_out.write(f_in.read())

    print(f"✅ Файл успешно распакован: {target_path}")
    return target_path

  def extract_from_memory(self, source_buffer: io.BytesIO, target_dir: str, output_filename: str) -> str:
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, output_filename)

    print(f"📦 Распаковка GZ из оперативной памяти в файл: {target_path}")

    # Распаковываем gzip-поток и записываем на диск
    with gzip.GzipFile(fileobj=source_buffer, mode="rb") as f_in, open(target_path, "wb") as f_out:
      f_out.write(f_in.read())

    print(f"✅ Успешно распаковано из памяти: {target_path}")
    return target_path

  @staticmethod
  def decompress_to_memory(source_buffer: io.BytesIO) -> io.BytesIO:
    """Чистая распаковка GZ из памяти в память (без записи на диск)."""
    print("📦 Распаковка GZ-потока в оперативной памяти...")
    unpacked_buffer = io.BytesIO()
    
    with gzip.GzipFile(fileobj=source_buffer, mode="rb") as f_in:
      unpacked_buffer.write(f_in.read())
      
    unpacked_buffer.seek(0)
    print("✅ Распаковка в памяти завершена.")
    return unpacked_buffer