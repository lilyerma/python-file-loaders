from pyspark.sql import DataFrame
from pyspark.sql.functions import col, date_format, count, rank, desc
from pyspark.sql.window import Window

def run(df: DataFrame) -> DataFrame:
    """Запрос 3: Самая популярная стартовая станция для каждого месяца."""
    df_with_month = df.withColumn(
        'year_month', date_format(col('start_time'), 'yyyy-MM')
    )

    station_counts = (
        df_with_month
        .groupBy('year_month', 'from_station_id', 'from_station_name')
        .agg(count('trip_id').alias('trip_count'))
    )

    window_spec = (
        Window.partitionBy('year_month')
        .orderBy(desc('trip_count'))
    )

    ranked_stations = station_counts.withColumn(
        'rank', rank().over(window_spec)
    )

    df_q3 = (
        ranked_stations
        .filter(col('rank') == 1)
        .orderBy('year_month')
    )

    return df_q3