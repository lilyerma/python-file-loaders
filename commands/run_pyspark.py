from pyspark_task.analytics import run_pyspark_pipeline

def register_command(subparsers):
    """Регистрация команды для запуска PySpark-анализа."""
    parser = subparsers.add_parser(
        "run-pyspark", 
        help="Запустить PySpark аналитический пайплайн по ZIP-архиву"
    )
    parser.add_argument(
        "--zip", 
        type=str, 
        required=True, 
        help="Путь к ZIP-архиву (например, pyspark_task/data/Divvy_Trips_2019_Q4.zip)"
    )

    parser.add_argument(
        "--query", 
        required=False, 
        default=None, 
        help="Имя конкретного запроса для выполнения (например, q3, q7)"
    )

    parser.set_defaults(func=run)


def run(args):

    run_pyspark_pipeline(zip_path=args.zip, target_query=args.query)
