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
    """Запуск PySpark-анализа на основе пакета pyspark_task."""
    import logging
    from pyspark_task.spark_session import create_spark_session
    from pyspark_task.analytics import execute_full_pipeline

    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    print(f"🚀 Запуск PySpark-пайплайна для архива: {args.zip}")

    # Создаем Spark-сессию
    spark = create_spark_session("DivvyPySparkCLI")

    try:
        # Вся тяжелая логика (распаковка, кодировки, цикл по запросам q1-q6, сохранение) 
        # инкапсулирована внутри модуля analytics пакета pyspark_task
        execute_full_pipeline(spark, zip_path=args.zip, target_query=args.query)
        print("✅ Анализ успешно завершен! Результаты сохранены в папку results.")
    finally:
        spark.stop()