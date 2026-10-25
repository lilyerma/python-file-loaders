import logging
import time
import importlib
from pyspark.sql import DataFrame
from db_managers.db_factory import DBManagerFactory 
from pyspark_task.ingestion import read_target_csv_from_zip_to_spark


logger = logging.getLogger("PySparkTaskAnalytics")

def run_query_with_tracking(query_name: str, query_func, df: DataFrame, *args, **kwargs) -> DataFrame:
    """Универсальный трекер для каждого аналитического запроса."""
    start_time = time.time()
    logger.info("🚀 Запуск запроса: [%s]...", query_name)
    
    try:
        result_df = query_func(df, *args, **kwargs)
        elapsed_time = time.time() - start_time
        row_count = result_df.count()
        
        logger.info(
            "✨ Запрос [%s] УСПЕШНО выполнен за %.2f сек. Строк в результате: %d", 
            query_name, elapsed_time, row_count
        )
        return result_df
    except Exception as e:
        logger.error("❌ Ошибка в запросе [%s]: %s", query_name, e, exc_info=True)
        raise

def save_result_to_csv(df: DataFrame, filename: str, results_dir: str = "results"):
    """Сохранение датафрейма в единый CSV."""
    output_path = f"{results_dir}/{filename}"
    logger.info("💾 Сохранение результата в: %s...", output_path)
    (
        df.coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .csv(output_path)
    )

def _get_query_modules(target_query: str = None) -> list[str]:
    """Определяет список модулей запросов для выполнения."""
    if target_query:
        return [target_query.lower()]
    return ["q1", "q2", "q3", "q4", "q5", "q6"]

def _execute_single_query(q_name: str, df: DataFrame) -> None:
    """Динамически загружает, выполняет и сохраняет отдельный аналитический запрос."""
    try:
        module = importlib.import_module(f"pyspark_task.queries.{q_name}")
        
        if not hasattr(module, "run"):
            logger.warning("⚠️ Модуль %s не содержит функции run(df)!", q_name)
            return

        result_df = run_query_with_tracking(
            query_name=f"Query_{q_name.upper()}",
            query_func=module.run,
            df=df
        )
        save_result_to_csv(result_df, f"{q_name}_result")
        
    except ModuleNotFoundError:
        logger.warning("⚠️ Файл запроса %s.py не найден в папке queries. Пропускаем.", q_name)
    except Exception as e:
        logger.error("💥 Ошибка при выполнении запроса %s: %s", q_name, e)

def run_pyspark_pipeline(zip_path: str, target_query: str = None):
    """Главная функция пайплайна: управляет ресурсами (фабрика) и оркестрирует шаги."""
    logger.info("🏁 Старт выполнения пайплайна для архива: %s", zip_path)

    # 1. Создаем Spark-менеджер через единую фабрику
    spark_manager = DBManagerFactory.create_manager("spark", app_name="PySparkCLI")
    spark = spark_manager.connect()
    
    try:
        # 2. Загружаем данные в Spark DataFrame через ин-момори чтение
        df = read_target_csv_from_zip_to_spark(spark, zip_path)
        
        # 3. Получаем список задач и последовательно их выполняем
        query_modules = _get_query_modules(target_query)
        for q_name in query_modules:
            _execute_single_query(q_name, df)

        logger.info("🎉 Пайплайн успешно завершен!")
    
    finally:
        # 4. Гарантированно закрываем менеджер через стандартизированный метод
        spark_manager.close()
        logger.info("🛑 Сессия Spark закрыта через менеджер.")