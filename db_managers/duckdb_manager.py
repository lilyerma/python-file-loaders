import duckdb
import pandas as pd
from contextlib import contextmanager
from db_managers.base import BaseDBManager
from db_managers.db_factory import DBManagerFactory

class DuckDBManager(BaseDBManager):

    def __init__(self, db_path: str = ":memory:"):
        """
        Инициализирует менеджер DuckDB.
        По умолчанию открывает базу в оперативной памяти (':memory:'), 
        либо принимает путь к файлу (например, 'analytics.duckdb').
        """
        self.db_path = db_path

    def connect(self):
        """Возвращает прямое соединение с DuckDB."""
        return duckdb.connect(self.db_path)

    @contextmanager
    def transaction(self):
        """
        Контекстный менеджер для безопасных транзакций в DuckDB.
        """
        con = duckdb.connect(self.db_path)
        try:
            # Явно стартуем транзакцию, чтобы rollback работал корректно
            con.execute("BEGIN TRANSACTION")
            yield con
            # Если всё прошло успешно, фиксируем изменения
            con.execute("COMMIT")
        except Exception as e:
            # Теперь транзакция точно активна, rollback выполнится без ошибок
            try:
                con.execute("ROLLBACK")
            except Exception:
                pass
            raise e
        finally:
            con.close()

    def save_dataframe(self, df, table_name: str, mode: str = "append"):
        """
        Сохранение DataFrame (Pandas или PySpark) в таблицу DuckDB.
        """
        # Если передан PySpark DataFrame, конвертируем в Pandas
        if hasattr(df, "toPandas"):
            df = df.toPandas()

        with self.connect() as con:
            if mode == "replace":
                con.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # DuckDB великолепно умеет регистрировать Pandas DataFrame как виртуальную таблицу
            # и записывать её в постоянную таблицу одной командой
            con.register("df_temp", df)
            con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df_temp")
            # Если таблица уже была и режим append:
            if mode == "append":
                con.execute(f"INSERT INTO {table_name} SELECT * FROM df_temp")
            con.unregister("df_temp")

    def close(self):
        # Для DuckDB соединение открывается локально под конкретную задачу,
        # поэтому здесь можно оставить pass или очищать кэш, если требуется.
        pass

    def save_query_to_csv(self, query_or_table: str, output_path: str, is_table: bool = True):
        """
        Сохраняет результат SQL-запроса или целую таблицу в CSV-файл.
        """
        # Если передан просто имя таблицы, оборачиваем в SELECT *
        sql = f"SELECT * FROM {query_or_table}" if is_table else query_or_table
        
        with self.connect() as con:
            # DuckDB позволяет экспортировать прямо в CSV на уровне движка (очень быстро)
            con.execute(f"COPY ({sql}) TO '{output_path}' (HEADER, DELIMITER ',');")
        print(f"📁 Данные успешно сохранены в CSV: {output_path}")

DBManagerFactory.register("duckdb", DuckDBManager)