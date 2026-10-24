# import os
# import zipfile
# import logging
# from pyspark.sql import SparkSession, DataFrame
# from pyspark.sql.functions import col, input_file_name, regexp_replace, split, element_at, when, regexp_extract

# logger = logging.getLogger("Ingestion")

# def read_target_csv_from_zip_to_spark(spark: SparkSession, zip_path: str, temp_dir: str = "./temp_extracted") -> DataFrame:
#     if not os.path.exists(zip_path):
#         raise FileNotFoundError(f"Архив не найден: {zip_path}")

#     # ИСПРАВЛЕНИЕ: Корректно убираем расширение, даже если оно двойное (.csv.zip)
#     base_name = os.path.basename(zip_path)
#     if base_name.endswith(".zip"):
#         zip_name = base_name[:-4]  # отрезаем .zip
#     else:
#         zip_name = base_name
    
#     # Если на конце осталась точка с csv (например, ...failures.csv), убираем и её для поиска внутри архива
#     search_query = zip_name[:-4] if zip_name.endswith(".csv") else zip_name

#     os.makedirs(temp_dir, exist_ok=True)

#     with zipfile.ZipFile(zip_path, 'r') as zf:
#         all_csvs = [
#             name for name in zf.namelist() 
#             if name.endswith('.csv') and '__MACOSX' not in name and not os.path.basename(name).startswith('.')
#         ]
        
#         if not all_csvs:
#             raise ValueError(f"В архиве {zip_path} не найдено подходящих CSV-файлов.")
        
#         # Ищем файл, имя которого похоже на имя архива
#         target_file = next((f for f in all_csvs if search_query.lower() in f.lower()), all_csvs[0])
#         logger.info("📄 Целевой файл в архиве: %s -> %s", zip_path, target_file)
        
#         extracted_file_path = os.path.join(temp_dir, target_file)
        
#         # Защита от ошибки с существующей директорией
#         if os.path.exists(extracted_file_path):
#             if os.path.isdir(extracted_file_path):
#                 shutil.rmtree(extracted_file_path)
#             else:
#                 os.remove(extracted_file_path)

#         zf.extract(target_file, path=temp_dir)


#     logger.info("   ✅ Файл успешно распакован во временную зону: %s", extracted_file_path)

import io
import zipfile
import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, input_file_name, regexp_extract, split, element_at, when, regexp_replace

logger = logging.getLogger("Ingestion")

def read_target_csv_from_zip_to_spark(spark: SparkSession, zip_path: str) -> DataFrame:
    """
    Читает целевой CSV из ZIP-архива напрямую в оперативной памяти (без сохранения на диск),
    используя Spark RDD (binaryFiles) и Python zipfile.
    """
    sc = spark.sparkContext
    logger.info("📦 Чтение архива в памяти без распаковки на диск: %s", zip_path)

    # Функция, выполняющаяся на воркере: распаковывает архив из байтов в памяти и стримит строчки
    def extract_lines(item):
        _, content = item
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            # Ищем все CSV файлы, исключая скрытые и макосовские
            all_csvs = [
                n for n in z.namelist() 
                if n.endswith('.csv') and '__MACOSX' not in n and not n.split('/')[-1].startswith('.')
            ]
            if not all_csvs:
                return
            
            # Берем первый подходящий CSV (или можно настроить фильтрацию по имени)
            target_csv = all_csvs[0]
            
            with z.open(target_csv) as f:
                for line in io.TextIOWrapper(f, encoding="utf-8"):
                    yield line.rstrip("\r\n")

    try:
        # 1. Читаем архив как бинарный файл в RDD и извлекаем строки
        lines_rdd = sc.binaryFiles(zip_path).flatMap(extract_lines)
        
        # 2. Превращаем RDD строк в DataFrame через Spark CSV reader
        spark_df = spark.read.csv(lines_rdd, header=True, inferSchema=True)
        
    except Exception as e:
        logger.error("💥 Ошибка при чтении архива в памяти %s: %s", zip_path, e)
        raise

    # 3. Добавляем метаданные из имени файла архива (т.к. input_file_name() для binaryFiles вернет путь к самому .zip)
    # Вытаскиваем имя архива в качестве source_file
    import os
    archive_filename = os.path.basename(zip_path)
    # Превращаем имя вида hard-drive-2022-01-01-failures.csv.zip в нормальное имя csv для source_file
    csv_mock_name = archive_filename[:-4] if archive_filename.endswith(".zip") else archive_filename
    if csv_mock_name.endswith(".csv.zip"):
        csv_mock_name = csv_mock_name[:-4]

    spark_df = spark_df.withColumn("source_file", regexp_extract(spark_df.columns[0], "", 0)) # заглушка или подставляем имя
    # # Или проставим имя файла через lit:
    # from pyspark.sql.functions import lit
    # spark_df = spark_df.withColumn("source_file", lit(csv_mock_name.replace(".zip", "")))

    # # Читаем CSV напрямую в PySpark DataFrame с автоопределением схемы и заголовка
    # # Используем encoding="UTF-8" (или "ISO-8859-1" / latin1 если потребуется)
    # spark_df = (
    #     spark.read
    #     .option("header", "true")
    #     .option("inferSchema", "true")
    #     .option("charset", "UTF-8")
    #     .csv(extracted_file_path)
    # )

    # Добавляем колонку с именем исходного файла из метаданных пути Spark
    spark_df = spark_df.withColumn(
        "source_file", 
        element_at(split(input_file_name(), "/"), -1)
    )

    # 2. Извлекаем дату из имени файла в колонку extracted_date
    spark_df = spark_df.withColumn(
        "extracted_date",
        regexp_extract(col("source_file"), r"(\d{4}-\d{2}-\d{2})", 1)
    )

    # 3. Проверяем её на пустую строку и заменяем на None
    spark_df = spark_df.withColumn(
        "extracted_date",
        when(col("extracted_date") == "", None).otherwise(col("extracted_date"))
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