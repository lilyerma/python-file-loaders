from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, to_date

def run(df: DataFrame) -> DataFrame:
    """
    Запрос 1: Вычисляет среднюю длительность поездки за каждый день.
    """
    # Шаг 1: Конвертируем колонку с датой начала поездки в тип date
    df_with_date = df.withColumn('trip_date', to_date(col('start_time')))

    # Шаг 2: Группируем по дате, считаем среднее и приводим к double
    df_q1 = (
        df_with_date
        .groupBy('trip_date')
        .agg(avg('tripduration').cast('double').alias('avg_tripduration'))
        .orderBy('trip_date')
    )

    return df_q1