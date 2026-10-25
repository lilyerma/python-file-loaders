import logging
from pathlib import Path
from db_managers.parquet_exporter import ParquetExporter
from db_managers.sql_runner import SqlScriptRunner

logger = logging.getLogger("CLI.ParquetRun")

def register_command(subparsers):

    p_parquet = subparsers.add_parser("parquet-run", help="Выполнить один SQL-файл и сохранить результат в Parquet")
    p_parquet.add_argument("--db-type", "-t", type=str, default="duckdb", help="Тип базы данных")
    p_parquet.add_argument("--file", "-f", type=str, required=True, help="Путь к конкретному .sql файлу")
    p_parquet.add_argument("--output", "-o", type=str, required=True, help="Путь для сохранения parquet-файла/директории")
    p_parquet.add_argument("--partition-by", "-p", type=str, nargs="*", help="Колонки для партиционирования (через пробел)")
    p_parquet.set_defaults(func=run)


def run(args):
    """Точечный экспорт SQL-файла в Parquet."""
    logger.info("📦 Экспорт SQL файла [%s] в Parquet (БД: %s)", args.file, args.db_type)
    try:
        # Инициализируем ранер для получения менеджера БД
        runner = SqlScriptRunner(db_type=args.db_type)
        
        # Используем отдельный класс экспортера
        exporter = ParquetExporter(db_manager=runner.db_manager)
        
        exporter.export_sql_file(
            sql_file_path=args.file,
            output_path=args.output,
            partition_by=args.partition_by
        )
        
        logger.info("🎉 Экспорт в Parquet успешно завершен!")
    except Exception as e:
        logger.error("❌ Ошибка при экспорте в Parquet: %s", e)
        raise e