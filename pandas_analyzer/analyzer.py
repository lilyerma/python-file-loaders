from pathlib import Path
import pandas as pd
from csv_to_pg_loader.ddl_generator import PostgresDdlGenerator 


class CsvAnalyzer:
  """Класс для рекурсивного поиска CSV-файлов и анализа их содержимого."""

  def __init__(self, root_dir: str | Path | None = None, ddl_output_dir: str | Path | None = None):
    self.root_dir = Path(root_dir) if root_dir else None
    self.ddl_generator = PostgresDdlGenerator(output_dir=ddl_output_dir)

  def analyze_dataframe(self, df: pd.DataFrame, table_name: str) -> None:
    """Анализирует готовый Pandas DataFrame, выводит статистику и генерирует DDL."""
    print(f"\n{'='*60}")
    print(f"📊 Таблица / Источник: {table_name}")
    print(f"{'='*60}")

    try:
      rows_count, cols_count = df.shape
      print(f"📊 Всего строк: {rows_count} | Колонок: {cols_count}")

      if rows_count == 0:
        print("⚠️ Данные отсутствуют.")
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

      # Генерация DDL
      clean_table_name = table_name.lower().replace("-", "_").replace(".", "_")
      ddl_script = self.ddl_generator.generate_from_dataframe(df, clean_table_name)

      print(f"\n--- Сгенерированный DDL ({clean_table_name}) ---")
      print(ddl_script)

      # Сохраняем в .sql файл
      saved_path = self.ddl_generator.save_ddl_to_file(ddl_script, clean_table_name)
      if saved_path:
        print(f"💾 DDL успешно сохранен в файл: {saved_path}")

    except Exception as e:
      print(f"[ERROR] Не удалось проанализировать датафрейм {table_name}: {e}")

  def analyze_file(self, csv_path: Path) -> None:
    """Оставляем метод для обратной совместимости с файлами на диске."""
    try:
      df = pd.read_csv(csv_path)
      table_name = csv_path.stem
      self.analyze_dataframe(df, table_name)
    except Exception as e:
      print(f"[ERROR] Не удалось обработать файл {csv_path}: {e}")

  def run_analysis(self) -> None:
    if not self.root_dir:
      print("❌ Корневая директория не задана.")
      return
    csv_files = list(self.root_dir.rglob("*.csv"))
    if not csv_files:
      print(f"❌ В директории '{self.root_dir}' не найдено CSV-файлов.")
      return

    print(f"🔍 Найдено CSV-файлов: {len(csv_files)}. Запуск анализа...")
    for csv_path in csv_files:
      self.analyze_file(csv_path)