from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col, isnan

def run(df: DataFrame) -> DataFrame:

    # Фильтруем некорректные значения для строковой колонки gender
    df_valid = df.filter(
        col('gender').isNotNull() & 
        (col('gender') != "nan") & 
        (col('gender') != "")
    )

    """Запрос 5: Средняя длительность поездки в зависимости от пола."""
    df_q5 = (
        df_valid.groupBy('gender')
        .agg(avg('tripduration').cast('double').alias('avg_tripduration'))
    )

    return df_q5