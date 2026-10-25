import pandas as pd
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_managers.base import BaseDBManager
from db_managers.db_factory import DBManagerFactory

class PostgresManager(BaseDBManager):
    def __init__(self, connection_url: str):
        self.url = connection_url
        self.engine = create_engine(self.url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def connect(self):
        """Возвращает сырое соединение из пула SQLAlchemy."""
        return self.engine.connect()

    @contextmanager
    def transaction(self):
        """
        Контекстный менеджер для безопасных транзакций.
        Пример использования:
            with pg_manager.transaction() as conn:
                conn.execute(...)
        """
        connection = self.engine.connect()
        trans = connection.begin()
        try:
            yield connection
            trans.commit()  # Автокоммит при успешном выполнении
        except Exception as e:
            trans.rollback()  # Откат при ошибке
            raise e
        finally:
            connection.close()

    def save_dataframe(self, df, table_name: str, mode: str = "append"):
        """
        Сохранение DataFrame в PostgreSQL. 
        Поддерживает как Pandas DataFrame, так и PySpark DataFrame (автоматически конвертирует в Pandas).
        """
        # Если передан PySpark DataFrame, конвертируем в Pandas для записи через SQLAlchemy
        if hasattr(df, "toPandas"):
            df = df.toPandas()

        # SQLAlchemy to_sql для записи
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists=mode,  # 'append', 'replace', 'fail'
            index=False,
            method="multi"   # Ускоряет вставку пачками
        )

    def close(self):
        """Корректное закрытие пула соединений движка SQLAlchemy."""
        if self.engine:
            self.engine.dispose()

DBManagerFactory.register("postgres", PostgresManager)