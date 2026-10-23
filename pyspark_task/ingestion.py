import os
import zipfile
import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, regexp_replace

logger = logging.getLogger("Ingestion")

def read_target_csv_from_zip_to_spark(spark: SparkSession, zip_path: str, temp_dir: str = "./temp_extracted") -> DataFrame:
    """
    Распаковывает ZIP-архив средствами Python, находит нужный CSV 
    и читает его напрямую в PySpark DataFrame без использования Pandas.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Архив не найден: {zip_path}")

    zip_name = os.path.splitext(os.path.basename(zip_path))[0]

    # Создаем временную директорию для распаковки
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Фильтруем мусор macOS и папки
        all_csvs = [
            name for name in zf.namelist() 
            if name.endswith('.csv') and '__MACOSX' not in name and not os.path.basename(name).startswith('.')
        ]
        
        if not all_csvs:
            raise ValueError(f"В архиве {zip_path} не найдено подходящих CSV-файлов.")
        
        target_file = next((f for f in all_csvs if zip_name.lower() in f.lower()), all_csvs[0])
        logger.info("📄 Целевой файл в архиве: %s -> %s", zip_path, target_file)
        
        # Распаковываем конкретный файл на диск, чтобы Spark мог его прочитать
        extracted_file_path = zf.extract(target_file, path=temp_dir)

    logger.info("   ✅ Файл успешно распакован во временную зону: %s", extracted_file_path)

    # Читаем CSV напрямую в PySpark DataFrame с автоопределением схемы и заголовка
    # Используем encoding="UTF-8" (или "ISO-8859-1" / latin1 если потребуется)
    spark_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("charset", "UTF-8")
        .csv(extracted_file_path)
    )

    # Очищаем колонку tripduration от запятых тысяч (например, "2,818.0" -> "2818.0")
    # и переводим в числовой формат средствами Spark
    if "tripduration" in spark_df.columns:
        spark_df = spark_df.withColumn(
            "tripduration", 
            regexp_replace(col("tripduration"), ",", "").cast("double")
        )

    logger.info("   🚀 Данные успешно загружены в PySpark DataFrame (без Pandas).")
    return spark_df