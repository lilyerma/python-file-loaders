import logging
from pathlib import Path
from db_managers.base import BaseDBManager
from db_managers.db_factory import DBManagerFactory
from config import POSTGRES_URL, DUCKDB_PATH

logger = logging.getLogger("SqlScriptRunner")

class SqlScriptRunner:
    def __init__(self, db_manager: BaseDBManager | None = None, db_type: str | None = None, **kwargs):
        if db_manager:
            self.db_manager = db_manager
        elif db_type:
            db_type_lower = db_type.lower()
            
            if db_type_lower == "postgres" and "connection_url" not in kwargs:
                kwargs["connection_url"] = POSTGRES_URL
            elif db_type_lower == "duckdb" and "db_path" not in kwargs:
                kwargs["db_path"] = DUCKDB_PATH

            self.db_manager = DBManagerFactory.create_manager(db_type_lower, **kwargs)
        else:
            raise ValueError("Необходимо передать либо готовый db_manager, либо db_type для фабрики.")
        
    def run_folder(self, sql_dir: str | Path, export_to_csv: bool = True) -> None:
        """
        Находит все .sql файлы в папке и последовательно выполняет их в базе данных.
        Если export_то_csv=True, результаты SELECT-запросов сохраняются в CSV.
        """
        sql_path = Path(sql_dir)

        if not sql_path.exists():
            logger.error("❌ Директория не найдена: %s", sql_path)
            return

        sql_files = sorted(sql_path.glob("*.sql"))

        if not sql_files:
            logger.warning("❌ В директории '%s' не найдено .sql файлов.", sql_path)
            return

        logger.info("🔍 Найдено SQL-скриптов: %d. Запускаем в базе данных...", len(sql_files))

        output_dir = Path("./output_csv")
        if export_to_csv:
            output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with self.db_manager.transaction() as conn:
                for file_path in sql_files:
                    logger.info("📄 Выполняется файл: %s", file_path.name)
                    
                    sql_content = file_path.read_text(encoding="utf-8").strip()
                    if not sql_content:
                        logger.warning("  Файл пуст, пропускаем.")
                        continue
                    
                    csv_path = output_dir / f"{file_path.stem}.csv" if export_to_csv else None
                    
                    # Выполняем запрос с возможным экспортом
                    self._execute_sql(conn, sql_content, csv_path)
                    
                    logger.info("✅ Успешно выполнено: %s", file_path.name)
                    
            logger.info("🎉 Все скрипты успешно применены!")
            
        except Exception as e:
            logger.error("💥 Процесс выполнения скриптов прерван из-за ошибки: %s", e)
            raise e

    def _execute_sql(self, conn, sql_content: str, csv_path: Path | None = None):
        """Вспомогательный метод для выполнения SQL-текста и выгрузки в CSV при необходимости."""
        
        # Если передан путь для экспорта и это DuckDB-подобное соединение, используем COPY
        if csv_path:
            # Очищаем запрос от лишних точек с запятой в конце, если они мешают обертке COPY
            clean_sql = sql_content.rstrip(";")
            
            try:
                # Пробуем выполнить через встроенный синтаксис DuckDB COPY (...) TO ...
                export_query = f"COPY ({clean_sql}) TO '{csv_path}' (HEADER, FORMAT CSV, DELIMITER ',')"
                conn.execute(export_query)
                return
            except Exception as export_err:
                # Если запрос не является SELECT-ом (например, CREATE/INSERT), COPY вызовет ошибку.
                # В таком случае падаем на обычное выполнение без экспорта.
                logger.debug("  Команда COPY неприменима (возможно, это не SELECT), выполняем стандартно: %s", export_err)

        # Стандартное выполнение (для DDL/DML запросов или если экспорт не требуется)
        try:
            from sqlalchemy import text
            if hasattr(conn, "execute") and not hasattr(conn, "cursor"): # Проверка на SQLAlchemy сессию
                conn.execute(text(sql_content))
                return
        except ImportError:
            pass

        # Для нативных коннекторов
        conn.execute(sql_content)