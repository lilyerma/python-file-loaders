from pyspark.sql import SparkSession

def create_spark_session(app_name: str = "ZipCsvPySparkAnalyzer") -> SparkSession:
    """
    Инициализирует и возвращает SparkSession для локальной или распределенной обработки.
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    # Устанавливаем уровень логирования, чтобы не засорять вывод консоли лишними ворнингами
    spark.sparkContext.setLogLevel("WARN")
    
    return spark