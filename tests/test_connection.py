from db_managers.db_factory import DBManagerFactory
from config import POSTGRES_URL
from sqlalchemy import text

def test_db_connection():
    print("🔄 Проверка подключения к PostgreSQL...")
    try:
        # Создаем менеджер через фабрику с использованием параметров из config.py
        db_manager = DBManagerFactory.create_manager("postgres", connection_url=POSTGRES_URL)
        
        # Используем соединение через менеджер
        with db_manager.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print("✅ Успешное подключение к базе данных!")
            print(f"📌 Версия PostgreSQL: {result[0]}")
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")

if __name__ == "__main__":
    test_db_connection()