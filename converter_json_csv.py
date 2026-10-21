import csv
import json
import os
from pathlib import Path


class RaggedJsonToCsvConverter:
  """Класс для рекурсивного обхода неоднородных директорий (ragged directories),

  поиска JSON-файлов и конвертации их в формат CSV.
  """

  def __init__(self, root_dir: str | Path):
    self.root_dir = Path(root_dir)

  def find_json_files(self) -> list[Path]:
    """Рекурсивно находит все файлы с расширением .json в директории."""
    return list(self.root_dir.rglob("*.json"))

  @staticmethod
  def convert_file(json_path: Path, csv_path: Path | None = None) -> Path:
    """Конвертирует один JSON-файл в CSV.

    Поддерживает как плоские JSON-объекты, так и списки объектов.
    """
    if csv_path is None:
      csv_path = json_path.with_suffix(".csv")

    with open(json_path, "r", encoding="utf-8") as f:
      data = json.load(f)

    # Приводим данные к списку словарей (если это единичный объект)
    if isinstance(data, dict):
      rows = [data]
    elif isinstance(data, list):
      rows = data
    else:
      raise ValueError(
          f"Неподдерживаемый формат данных в файле {json_path}: {type(data)}"
      )

    if not rows:
      # Если файл пустой, создаем пустой CSV
      csv_path.write_text("", encoding="utf-8")
      return csv_path

    # Собираем все уникальные ключи со всех строк (на случай разной структуры / ragged data)
    fieldnames = []
    for row in rows:
      if isinstance(row, dict):
        for key in row.keys():
          if key not in fieldnames:
            fieldnames.append(key)

    # Записываем данные в CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      for row in rows:
        if isinstance(row, dict):
          writer.writerow(row)

    print(f"[CONVERTED] {json_path} -> {csv_path}")
    return csv_path

  def process_all(self) -> list[Path]:
    """Запускает полный процесс поиска и конвертации всех JSON-файлов."""
    json_files = self.find_json_files()
    converted_files = []

    if not json_files:
      print(f"В директории '{self.root_dir}' не найдено JSON-файлов.")
      return converted_files

    print(
        f"Найдено JSON-файлов: {len(json_files)}. Начинаем конвертацию..."
    )
    for json_path in json_files:
      try:
        csv_path = self.convert_file(json_path)
        converted_files.append(csv_path)
      except Exception as e:
        print(f"[ERROR] Не удалось обработать файл {json_path}: {e}")

    return converted_files


if __name__ == "__main__":
  # Пример запуска для папки с данными
  target_directory = "./data"  # Замените на путь к вашим данным
  converter = RaggedJsonToCsvConverter(target_directory)
  converter.process_all()