import logging
import time
import importlib
from pyspark.sql import DataFrame, SparkSession
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

def execute_full_pipeline(spark: SparkSession, zip_path: str, target_query: str = None):
    """Главная функция пайплайна: загружает данные и выполняет запросы (все или конкретный)."""
    logger.info("🏁 Старт выполнения пайплайна для архива: %s", zip_path)
    
    # 1. Загружаем данные в Spark DataFrame
    df = read_target_csv_from_zip_to_spark(spark, zip_path)
    
    # 2. Определяем список запросов для выполнения
    if target_query:
        # Приводим к нижнему регистру для надежности (например, "Q3" -> "q3")
        query_modules = [target_query.lower()]
    else:
        query_modules = ["q1", "q2", "q3", "q4", "q5", "q6"]
    
    for q_name in query_modules:
        try:
            # Динамически импортируем модуль из папки queries (например, pyspark_task.queries.q1)
            module = importlib.import_module(f"pyspark_task.queries.{q_name}")
            
            if hasattr(module, "run"):
                # Запускаем с трекингом
                result_df = run_query_with_tracking(
                    query_name=f"Query_{q_name.upper()}",
                    query_func=module.run,
                    df=df
                )
                # Сохраняем результат в папку results под соответствующим именем
                save_result_to_csv(result_df, f"{q_name}_result")
            else:
                logger.warning("⚠️ Модуль %s не содержит функции run(df)!", q_name)
                
        except ModuleNotFoundError:
            logger.warning("⚠️ Файл запроса %s.py не найден в папке queries. Пропускаем.", q_name)
        except Exception as e:
            logger.error("💥 Ошибка при выполнении запроса %s: %s", q_name, e)

    logger.info("🎉 Пайплайн успешно завершен!")