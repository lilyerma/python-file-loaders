from pyspark.sql.functions import col, split, element_at, desc, concat_ws, sha2
from pyspark.sql import DataFrame

from pyspark.sql.window import Window
from pyspark.sql.functions import ntile

def run(df: DataFrame) -> DataFrame:
    """
    1. Создает вторичный датафрейм уникальных моделей и их емкости.
    2. Делит модели на 5 квантилей (пентилей) по capacity_bytes (от больших к меньшим).
    3. Джойнит полученный квантиль (storage_quantile_id) обратно в основной датафрейм.
    """
    df = df.select(
        "source_file",
        "extracted_date",
        "model",
        "capacity_bytes" 
    )

    # 1. Формируем вторичный датафрейм
    df_secondary = (
        df.select("model", "capacity_bytes")
        .dropna(subset=["model", "capacity_bytes"])
        .distinct()
    )

    # 2. Задаем оконную функцию с сортировкой от наибольшего объема к наименьшему
    window_spec = Window.orderBy(desc("capacity_bytes"))

    # 3. Применяем ntile(5) для разбиения на 5 квантилей
    # (1 - самые емкие диски, 5 - самые маленькие)
    df_quantiled = df_secondary.withColumn(
        "storage_quantile_id", 
        ntile(5).over(window_spec)
    )

    # 4. Возвращаем данные в главный датасет через левый джоин по модели
    df_main_enriched = df.join(
        df_quantiled.select("model", "storage_quantile_id"),
        on="model",
        how="left"
    )



    # # Define the columns that make a record unique
    # unique_cols = ["model", "capacity_bytes"]

    # # Create the primary_key column
    # df_main_enriched = df_main_enriched.withColumn(
    #     "primary_key", 
    #     sha2(concat_ws("_", *[col(c) for c in unique_cols]), 256)
    # )

    # df.select("primary_key", *unique_cols).show(5, truncate=False)


    q7 = df_main_enriched.withColumn(
        "brand", 
        element_at(split(col('model'), " "), 1)
    )

    return q7
