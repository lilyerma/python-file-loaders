import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
  """Менеджер для управления подключением к PostgreSQL."""

  def __init__(self, db_url: str | None = None):
    # Если URL не передан, берем из переменных окружения или используем дефолтный для Docker
    self.db_url = db_url or os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:secretpassword@postgres:5432/loader_db",
    )
    self.engine = create_engine(self.db_url)
    self.SessionLocal = sessionmaker(bind=self.engine)

  @contextmanager
  def get_connection(self):
    """Контекстный менеджер для получения сырого соединения (удобно для выполнения SQL-скриптов)."""
    connection = self.engine.connect()
    try:
      yield connection
      connection.commit()  # Автоматический коммит при успешном выполнении
    except Exception as e:
      connection.rollback()  # Откат при ошибке
      raise e
    finally:
      connection.close()