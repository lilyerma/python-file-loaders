from pathlib import Path
from sqlalchemy import text
from csv_to_pg_loader.db_manager import DatabaseManager


class SqlScriptRunner:
  """Класс для пакетного поиска и выполнения SQL-скриптов

  из указанной директории в базе данных PostgreSQL.
  """

  def __init__(self, db_manager: DatabaseManager | None = None):
    self.db_manager = db_manager or DatabaseManager()

  def run_folder(self, sql_dir: str | Path) -> None:
    """Рекурсивно или линейно находит все .sql файлы в папке

    и последовательно выполняет их в базе данных.
    """
    sql_path = Path(sql_dir)

    if not sql_path.exists():
      print(f"[ERROR] Директория не найдена: {sql_path}")
      return

    # Находим и сортируем все .sql файлы
    sql_files = sorted(sql_path.glob("*.sql"))

    if not sql_files:
      print(f"❌ В директории '{sql_path}' не найдено .sql файлов.")
      return

    print(f"🔍 Найдено SQL-скриптов: {len(sql_files)}. Запускаем в базе данных...")

    try:
      with self.db_manager.get_connection() as conn:
        for file_path in sql_files:
          print(f"📄 Выполняется файл: {file_path.name}")
          try:
            sql_content = file_path.read_text(encoding="utf-8")
            conn.execute(text(sql_content))
            print(f"✅ Успешно выполнено: {file_path.name}")
          except Exception as e:
            print(f"❌ Ошибка при выполнении файла {file_path.name}: {e}")
            raise e
      print("🎉 Все миграции успешно применены!")
    except Exception as e:
      print("[ERROR] Процесс выполнения миграций прерван из-за ошибки.")