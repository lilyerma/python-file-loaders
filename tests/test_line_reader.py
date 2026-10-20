"""Тесты для универсальной читалки LineReader."""

import io
import pytest
from readers.line_reader import LineReader


def test_line_reader_with_stream_variable_mode():
  """Проверяем режим 'variable' на потоке BytesIO/StringIO."""
  stream = io.StringIO("header_col1,header_col2\nrow1_val1,row1_val2\n")

  first_line = LineReader.read_stream(stream, mode="variable")

  assert first_line == "header_col1,header_col2"


def test_line_reader_with_file(tmp_path):
  """Проверяем чтение реального файла с диска."""
  file_path = tmp_path / "sample.csv"
  file_path.write_text("line1\nline2\nline3\n", encoding="utf-8")

  # Проверяем, что в режиме variable читается именно первая строка
  first_line = LineReader.read_stream(str(file_path), mode="variable")
  assert first_line == "line1"