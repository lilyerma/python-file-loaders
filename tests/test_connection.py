from csv_to_pg_loader.db_manager import DatabaseManager
from sqlalchemy import text

def test_db_connection():
    print("🔄 Проверка подключения к PostgreSQL...")
    try:
        db = DatabaseManager()
        # Используем наш контекстный менеджер соединения
        with db.get_connection() as conn:
            # Выполняем простой тестовый запрос
            result = conn.execute(text("SELECT version();")).fetchone()
            print("✅ Успешное подключение к базе данных!")
            print(f"📌 Версия PostgreSQL: {result[0]}")
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")

if __name__ == "__main__":
    test_db_connection()