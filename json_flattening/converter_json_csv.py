import csv
import json
from pathlib import Path


class RaggedJsonToCsvConverter:
  """Класс для рекурсивного обхода неоднородных директорий (ragged directories),

  поиска JSON-файлов, флаттенинга вложенных структур и конвертации в CSV.
  """

  def __init__(self, root_dir: str | Path, output_dir: str | Path | None = None):
    self.root_dir = Path(root_dir)
    self.output_dir = Path(output_dir) if output_dir else None
    if self.output_dir:
      self.output_dir.mkdir(parents=True, exist_ok=True)

  def find_json_files(self) -> list[Path]:
    """Рекурсивно находит все файлы с расширением .json в директории."""
    return list(self.root_dir.rglob("*.json"))

  @staticmethod
  def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    """Рекурсивно разворачивает многоуровневый (вложенный) словарь

    в плоский словарь с составными ключами (например, info_city).
    """
    items = []
    for k, v in d.items():
      new_key = f"{parent_key}{sep}{k}" if parent_key else k
      if isinstance(v, dict):
        items.extend(RaggedJsonToCsvConverter.flatten_dict(v, new_key, sep=sep).items())
      else:
        items.append((new_key, v))
    return dict(items)

  def convert_file(self, json_path: Path) -> Path:
    """Конвертирует JSON-файл в CSV с предварительным флаттенингом данных."""
    if self.output_dir:
      csv_path = self.output_dir / json_path.with_suffix(".csv").name
    else:
      csv_path = json_path.with_suffix(".csv")

    with open(json_path, "r", encoding="utf-8") as f:
      data = json.load(f)

    # Приводим данные к списку словарей
    
    if isinstance(data, dict):
      rows = [data]
    elif isinstance(data, list):
      rows = data
    else:
      raise ValueError(
          f"Неподдерживаемый формат данных в файле {json_path}: {type(data)}"
      )

    if not rows:
      csv_path.write_text("", encoding="utf-8")
      return csv_path

    # Применяем flattening к каждой строке и собираем все уникальные ключи
    flattened_rows = []
    fieldnames = []

    for row in rows:
      if isinstance(row, dict):
        flat_row = self.flatten_dict(row)
      else:
        # Если элемент — примитив (число, строка), заворачиваем в дефолтный ключ
        flat_row = {"value": row}

      flattened_rows.append(flat_row)
      for key in flat_row.keys():
        if key not in fieldnames:
          fieldnames.append(key)

    # Записываем плоские данные в CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      for row in flattened_rows:
        writer.writerow(row)

    print(f"[CONVERTED & FLATTENED] {json_path} -> {csv_path}")
    return csv_path

  def process_all(self) -> list[Path]:
    """Запускает полный процесс поиска, флаттенинга и конвертации."""
    json_files = self.find_json_files()
    converted_files = []

    if not json_files:
      print(f"В директории '{self.root_dir}' не найдено JSON-файлов.")
      return converted_files

    print(
        f"Найдено JSON-файлов: {len(json_files)}. Начинаем флаттенинг и конвертацию..."
    )
    for json_path in json_files:
      try:
        csv_path = self.convert_file(json_path)
        converted_files.append(csv_path)
      except Exception as e:
        print(f"[ERROR] Не удалось обработать файл {json_path}: {e}")

    return converted_files


if __name__ == "__main__":
  # Пример запуска
  converter = RaggedJsonToCsvConverter(
      root_dir="json_flattening/data", output_dir="./output_csv"
  )
  converter.process_all()