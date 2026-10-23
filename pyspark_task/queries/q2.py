from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, to_date

def run(df: DataFrame) -> DataFrame:
    """Запрос 2: Количество поездок за каждый день."""
    df_with_date = df.withColumn('trip_date', to_date(col('start_time')))
    
    df_q2 = (
        df_with_date
        .groupBy('trip_date')
        .agg(count('trip_id').alias('num_of_trips'))
        .orderBy('trip_date')
    )
    
    return df_q2