import logging
from pathlib import Path

logger = logging.getLogger("ParquetExporter")

class ParquetExporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def export_sql_file(
        self, 
        sql_file_path: str | Path, 
        output_path: str | Path, 
        partition_by: list[str] | None = None
    ) -> None:
        """
        Принимает один SQL-файл, выполняет его через текущий менеджер БД 
        и сохраняет результат в Parquet с опциональными партициями.
        """
        file_path = Path(sql_file_path)
        out_path = Path(output_path)

        if not file_path.exists():
            logger.error("❌ SQL-файл не найден: %s", file_path)
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        sql_content = file_path.read_text(encoding="utf-8").strip()
        if not sql_content:
            logger.warning("❌ Файл '%s' пуст.", file_path.name)
            return

        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("📄 Экспорт запроса из файла %s в Parquet...", file_path.name)

        try:
            with self.db_manager.transaction() as conn:
                clean_sql = sql_content.rstrip(";")

                partition_clause = ""
                if partition_by:
                    cols = ", ".join(partition_by)
                    partition_clause = f", PARTITION_BY ({cols})"

                # Нативная команда DuckDB для экспорта
                export_query = f"COPY ({clean_sql}) TO '{out_path}' (FORMAT PARQUET{partition_clause})"
                
                # Поддержка разных типов коннекторов
                if hasattr(conn, "execute"):
                    conn.execute(export_query)
                else:
                    raise TypeError("Переданный объект соединения не поддерживает метод execute().")
                
            logger.info("✅ Успешно сохранено в Parquet: %s", out_path)
            
        except Exception as e:
            logger.error("💥 Ошибка при экспорте файла %s в Parquet: %s", file_path.name, e)
            raise e