from pathlib import Path
import pandas as pd
from csv_to_pg_loader.ddl_generator import PostgresDdlGenerator 


class CsvAnalyzer:
  """Класс для рекурсивного поиска CSV-файлов и анализа их содержимого."""

  def __init__(
      self, root_dir: str | Path, ddl_output_dir: str | Path | None = None
  ):
    self.root_dir = Path(root_dir)
    # Инициализируем генератор DDL (можно указать папку, куда складывать .sql файлы)
    self.ddl_generator = PostgresDdlGenerator(output_dir=ddl_output_dir)

  def find_csv_files(self) -> list[Path]:
    """Рекурсивно находит все файлы с расширением .csv в директории."""
    return list(self.root_dir.rglob("*.csv"))

  def analyze_file(self, csv_path: Path) -> None:
    """Анализирует CSV-файл, выводит статистику и генерирует DDL."""
    print(f"\n{'='*60}")
    print(f"📁 Файл: {csv_path}")
    print(f"{'='*60}")

    try:
      df = pd.read_csv(csv_path)
      rows_count, cols_count = df.shape
      print(f"📊 Всего строк: {rows_count} | Колонок: {cols_count}")

      if rows_count == 0:
        print("⚠️ Файл пуст.")
        return

      # Сбор аналитики по колонкам
      column_stats = []
      for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / rows_count) * 100

        min_val, max_val = "N/A", "N/A"
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
          if df[col].notnull().any():
            min_val = df[col].min()
            max_val = df[col].max()
        else:
          non_null_strs = df[col].dropna().astype(str)
          if not non_null_strs.empty:
            lengths = non_null_strs.str.len()
            min_val = f"мин. длина: {lengths.min()}"
            max_val = f"макс. длина: {lengths.max()}"

        column_stats.append({
            "Колонка": col,
            "Тип данных": str(dtype),
            "Null / NaN": f"{null_count} ({null_percentage:.1f}%)",
            "Min": min_val,
            "Max": max_val,
        })

      # Вывод таблицы со статистикой
      stats_df = pd.DataFrame(column_stats)
      print("\n--- Детальный отчет по колонкам ---")
      print(stats_df.to_string(index=False))

      # Генерация DDL через выделенный класс
      table_name = csv_path.stem.lower().replace("-", "_")
      ddl_script = self.ddl_generator.generate_from_dataframe(df, table_name)

      print(f"\n--- Сгенерированный DDL ({table_name}) ---")
      print(ddl_script)

      # Опционально сохраняем в отдельный .sql файл, если задана папка
      saved_path = self.ddl_generator.save_ddl_to_file(ddl_script, table_name)
      if saved_path:
        print(f"💾 DDL успешно сохранен в файл: {saved_path}")

    except Exception as e:
      print(f"[ERROR] Не удалось обработать файл {csv_path}: {e}")

  def run_analysis(self) -> None:
    csv_files = self.find_csv_files()
    if not csv_files:
      print(f"❌ В директории '{self.root_dir}' не найдено CSV-файлов.")
      return

    print(f"🔍 Найдено CSV-файлов: {len(csv_files)}. Запуск анализа...")
    for csv_path in csv_files:
      self.analyze_file(csv_path)


if __name__ == "__main__":
  target_path = Path("python-file-loaders/csv_to_pg_loader/data")
  # Указываем директорию, куда складывать готовые SQL-файлы миграций
  analyzer = CsvAnalyzer(
      root_dir=target_path, ddl_output_dir="python-file-loaders/csv_to_pg_loader/sql"
  )
  analyzer.run_analysis()