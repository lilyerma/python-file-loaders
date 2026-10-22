from pathlib import Path
import pandas as pd


class PostgresDdlGenerator:
  """Класс для генерации PostgreSQL DDL-скриптов

  на основе структуры данных DataFrame или словаря колонок.
  """

  # Словарь маппинга типов Pandas -> PostgreSQL
  PANDAS_TO_PG_TYPES = {
      "int64": "BIGINT",
      "int32": "INTEGER",
      "int16": "SMALLINT",
      "float64": "DOUBLE PRECISION",
      "float32": "REAL",
      "bool": "BOOLEAN",
      "datetime64[ns]": "TIMESTAMP",
      "object": "TEXT",
  }

  def __init__(self, output_dir: str | Path | None = None):
    self.output_dir = Path(output_dir) if output_dir else None
    if self.output_dir:
      self.output_dir.mkdir(parents=True, exist_ok=True)

  def generate_from_dataframe(
      self, df: pd.DataFrame, table_name: str | None = None
  ) -> str:
    """Генерирует текст SQL-запроса CREATE TABLE из DataFrame.
    
    """
    if df.empty or len(df.columns) == 0:
      raise ValueError("DataFrame пуст, невозможно сгенерировать DDL.")

    df.columns = df.columns.str.strip()

    columns = list(df.columns)
    pk_col = columns[0]

    ddl_lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    columns_def = []

  
    # 1. Перечисляем ВСЕ колонки по порядку
    for col in columns:
      pd_type = str(df[col].dtype)
      pg_type = self.PANDAS_TO_PG_TYPES.get(pd_type, "TEXT")
      safe_col_name = f'"{col}"'
      columns_def.append(f"    {safe_col_name} {pg_type}")

    # 2. Добавляем CONSTRAINT для Primary Key в конец и шаблон для FK
    pk_constraint_name = f"pk_{table_name}_{pk_col}"
    columns_def.append(
        f'    CONSTRAINT "{pk_constraint_name}" PRIMARY KEY ("{pk_col}"),'
        f'    CONSTRAINT name_of_the_fk_constraint FOREIGN KEY (name_of_the_key) '
        f'REFERENCES name_of_the_f_table (name_of_the_key) ON DELETE CASCADE'
    )

    # Собираем всё воедино
    ddl_lines.append(",\n".join(columns_def))
    ddl_lines.append(");\n")

    return "\n".join(ddl_lines)

  def save_ddl_to_file(self, ddl_script: str, table_name: str) -> Path | None:
    """Сохраняет сгенерированный DDL-скрипт в отдельный .sql файл."""
    if not self.output_dir:
      return None

    sql_path = self.output_dir / f"{table_name}.sql"
    sql_path.write_text(ddl_script, encoding="utf-8")
    return sql_path