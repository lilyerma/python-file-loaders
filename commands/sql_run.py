def run(args):
    """Запуск SQL-скриптов в PostgreSQL."""
    from csv_to_pg_loader.db_manager import DatabaseManager
    from csv_to_pg_loader.sql_runner import SqlScriptRunner

    db_manager = DatabaseManager()
    runner = SqlScriptRunner(db_manager=db_manager)
    runner.run_folder(args.dir)