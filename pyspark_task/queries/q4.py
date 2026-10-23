from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, date_sub, lit, rank, desc, to_date
from pyspark.sql.functions import max as spark_max
from pyspark.sql.window import Window

def run(df: DataFrame) -> DataFrame:
    """Запрос 4: Топ-3 станции отправления за последние 14 дней."""
    df_with_date = df.withColumn('trip_date', to_date(col('start_time')))
    
    max_date = df_with_date.select(spark_max('trip_date')).collect()[0][0]

    station_counts_date = (
        df_with_date
        .groupBy('trip_date', 'from_station_name')
        .agg(count('trip_id').alias('trip_count'))
        .filter(col('trip_date') >= date_sub(lit(max_date), 14))
    )

    window_spec = (
        Window.partitionBy('trip_date')
        .orderBy(desc('trip_count'))
    )

    ranked_stations_date = station_counts_date.withColumn(
        'rank', rank().over(window_spec)
    )

    df_q4 = (
        ranked_stations_date
        .filter(col('rank') <= 3)
        .orderBy(col('trip_date').desc(), col('rank').asc())
    )

    return df_q4