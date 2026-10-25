import logging
from db_managers.sql_runner import SqlScriptRunner

logger = logging.getLogger("CLI.SqlRun")

def register_command(subparsers):
    p_sql = subparsers.add_parser("sql-run", help="Запустить SQL-скрипты в указанной БД")
    
    # Пользователь указывает только тип базы и папку
    p_sql.add_argument("--db-type", "-t", type=str, default="postgres", help="Тип базы данных (postgres, duckdb)")
    p_sql.add_argument("--dir", "-d", type=str, required=True, help="Путь к директории с .sql файлами")
    
    p_sql.set_defaults(func=run)
    
def run(args):
    """Запуск SQL-скриптов."""
    logger.info("🚀 Запуск скриптов для БД [%s] из директории: %s", args.db_type, args.dir)
    
    try:
        # Передаем только тип базы и папку. 
        # Всю грязную работу по выбору URL/путей из config.py берет на себя SqlScriptRunner.
        runner = SqlScriptRunner(db_type=args.db_type)
        runner.run_folder(args.dir)
        
        logger.info("🎉 Скрипты успешно выполнены!")
    except Exception as e:
        logger.error("❌ Ошибка при выполнении скриптов: %s", e)
        raise e
