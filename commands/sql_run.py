def register_command(subparsers):
    p_sql = subparsers.add_parser("sql-run", help="Запустить SQL скрипты в PostgreSQL")
    p_sql.add_argument("--dir", "-d", type=str, default="csv_to_pg_loader/sql", help="Путь к директории с .sql")
    p_sql.set_defaults(func=run)
    
def run(args):
    """Запуск SQL-скриптов в PostgreSQL."""
    from csv_to_pg_loader.db_manager import DatabaseManager
    from csv_to_pg_loader.sql_runner import SqlScriptRunner

    db_manager = DatabaseManager()
    runner = SqlScriptRunner(db_manager=db_manager)
    runner.run_folder(args.dir)