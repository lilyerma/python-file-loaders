"""Скрипт-эксперимент с переиспользованием существующего загрузчика (requests)."""

import io
import requests  # Предполагаем, что requests уже используется в проекте
from extractors.gz_extractor import GzipExtractor
from readers.line_reader import LineReader
from utils.profiler import memory_profiler


def download_via_requests_to_memory(url: str) -> io.BytesIO:
  """Загружает файл по HTTP/CloudFront через requests в оперативную память (BytesIO)

  потоково чанками, переиспользуя стандартные механизмы запросов.
  """
  print(f"📥 Скачивание через requests: {url} в RAM...")
  buffer = io.BytesIO()

  # Используем stream=True для эффективного потокового чтения чанками
  with requests.get(url, stream=True) as response:
    response.raise_for_status()  # Выбросит исключение, если статус не 200
    for chunk in response.iter_content(chunk_size=8192):
      if chunk:
        buffer.write(chunk)

  buffer.seek(0)
  print("✅ Файл успешно загружен в оперативную память.")
  return buffer


def run_experiment():
  BASE_URL = "https://data.commoncrawl.org"
  INITIAL_KEY = "crawl-data/CC-MAIN-2022-05/wet.paths.gz"
  initial_url = f"{BASE_URL}/{INITIAL_KEY}"

  print("🚀 Запуск эксперимента с переиспользованием загрузчика...")

  with memory_profiler("Полный цикл эксперимента"):

    # Шаг 1: Скачивание .gz файла через requests в память
    print(f"\n[Шаг 1] Скачивание индекса в RAM...")
    gz_buffer = download_via_requests_to_memory(initial_url)

    # Шаг 2: Распаковка .gz в памяти с помощью GzipExtractor
    print("\n[Шаг 2] Распаковка GZ-архива в памяти...")
    unpacked_buffer = GzipExtractor.decompress_to_memory(gz_buffer)

    # Шаг 3: Чтение первой строки (URI) через LineReader
    print("\n[Шаг 3] Чтение первой строки (URI)...")
    text_stream = io.TextIOWrapper(unpacked_buffer, encoding="utf-8")
    first_uri = LineReader.read_stream(text_stream, mode="variable")

    if not first_uri:
      print("❌ Не удалось извлечь URI.")
      return

    target_key = first_uri.strip()
    target_url = f"{BASE_URL}/{target_key}"
    print(f"🎯 Извлеченный целевой URL: {target_url}")

    # --- Шаг 4: Скачивание целевого файла по URI в оперативную память ---
    print(f"\n[Шаг 4] Скачивание целевого WET.GZ файла в RAM...")
    target_gz_buffer = download_via_requests_to_memory(target_url)

    # --- Шаг 4.1: Распаковка целевого архива в памяти ---
    print(f"\n[Шаг 4.1] Распаковка целевого WET.GZ архива в памяти...")
    target_unpacked_buffer = GzipExtractor.decompress_to_memory(target_gz_buffer)

    # --- Шаг 5: Потоковый вывод строк в stdout ---
    print(
        "\n[Шаг 5] Потоковый вывод строк распакованного WET-файла в stdout..."
    )
    target_text_stream = io.TextIOWrapper(
        target_unpacked_buffer, encoding="utf-8", errors="replace"
    )

    LineReader.read_stream(target_text_stream, mode="stdout")

  print("\n✨ Эксперимент успешно завершен!")


if __name__ == "__main__":
  run_experiment()