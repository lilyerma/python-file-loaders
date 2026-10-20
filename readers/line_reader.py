"""Модуль для построчного чтения файлов или потоков с поддержкой вывода в stdout

или сохранения первой строки в переменную.
"""

import os
from typing import IO, Optional, Union


class LineReader:
  """Универсальный построчный читатель для файлов и потоков."""

  @staticmethod
  def read_stream(
      stream: Union[str, IO[str], IO[bytes]],
      mode: str = "stdout",
      encoding: str = "utf-8",
  ) -> Optional[str]:
    """Читает источник (путь к файлу или открытый поток) построчно.

    Args:
        stream: Путь к файлу (str), либо открытый файлоподобный поток (IO).
        mode: Режим работы ('stdout' — вывод в консоль, 'variable' — вернуть
          первую строку).
        encoding: Кодировка текста (по умолчанию utf-8).

    Returns:
        str или None: Возвращает первую строку, если выбран режим 'variable',
        иначе None.
    """
    first_line = None

    # Определяем, передали ли нам путь к файлу на диске или готовый поток/файл
    if isinstance(stream, str):
      if not os.path.exists(stream):
        raise FileNotFoundError(f"Файл для чтения не найден: {stream}")
      print(f"📖 Открываем файл с диска для чтения: {stream}")
      file_context = open(stream, "r", encoding=encoding, errors="replace")
    else:
      # Это уже открытый поток (например, файл или BytesIO/TextIOWrapper)
      # Если поток передан в байтах, попробуем обернуть в текст или читать корректно
      if hasattr(stream, "readable") and not isinstance(stream, IO):
        pass
      file_context = stream

    try:
      for index, line in enumerate(file_context):
        # Если поток байтовый, декодируем в строку
        if isinstance(line, bytes):
          line = line.decode(encoding, errors="replace")

        line_stripped = line.rstrip("\r\n")

        # Запоминаем самую первую строку (индекс 0)
        if index == 0:
          first_line = line_stripped

        # Режим 1: Вывод в консоль (stdout)
        if mode == "stdout":
          print(f"[{index + 1}] {line_stripped}")

        # Режим 2: Если нам нужна только первая строка, можем прервать чтение после нее
        elif mode == "variable" and index == 0:
          print(f"📌 Первая строка сохранена в переменную: {first_line}")
          # В режиме variable для первой строки можно сразу выйти, если нужны только метаданные
          break

    finally:
      # Закрываем файл только если открывали его сами по строковому пути
      if isinstance(stream, str) and "file_context" in locals():
        file_context.close()
        print("🔒 Файл закрыт.")

    return first_line