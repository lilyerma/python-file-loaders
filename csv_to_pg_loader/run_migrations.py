from pathlib import Path
from sqlalchemy import text
from db_manager import DatabaseManager


def run_sql_folder(sql_dir: str | Path, db_manager: DatabaseManager) -> None:
  """Рекурсивно находит и выполняет все .sql файлы из указанной папки."""
  sql_path = Path(sql_dir)
  
  # Находим все sql файлы
  sql_files = sorted(sql_path.glob("*.sql"))

  if not sql_files:
    print(f"❌ В директории '{sql_path}' не найдено .sql файлов.")
    return

  print(f"🔍 Найдено SQL-скриптов: {len(sql_files)}. Начинаем выполнение...")

  # Открываем единое соединение для пачки скриптов
  with db_manager.get_connection() as conn:
    for file_path in sql_files:
      print(f"📄 Выполняется файл: {file_path.name}")
      try:
        # Читаем текст SQL-файла
        sql_content = file_path.read_text(encoding="utf-8")
        
        # Оборачиваем в text() для SQLAlchemy 2.x и выполняем
        conn.execute(text(sql_content))
        
        print(f"✅ Успешно выполнено: {file_path.name}")
      except Exception as e:
        print(f"❌ Ошибка при выполнении файла {file_path.name}: {e}")


if __name__ == "__main__":
  # Указываем путь к папке со сгенерированными ранее .sql скриптами
  target_sql_dir = Path("csv_to_pg_loader/sql")

  # Инициализируем менеджер базы данных
  db = DatabaseManager()

  # Запускаем цикл выполнения миграций
  run_sql_folder(target_sql_dir, db)