from pyspark.sql import DataFrame
from pyspark.sql.functions import col, date_format, avg, desc, asc, lit, isnan

def run(df: DataFrame) -> DataFrame:
    """Запрос 6: Топ-10 возрастов с самыми длинными и самыми короткими поездками."""
    df_with_year = df.withColumn(
        'trip_year', date_format(col('start_time'), 'yyyy').cast('int')
    )

# Шаг 2: Жестко фильтруем мусор, null, пустые строки и NaN в birthyear и start_time
    df_valid = df_with_year.filter(
        col('birthyear').isNotNull() & 
        col('start_time').isNotNull() &
        ~isnan(col('birthyear'))
    )

    # Шаг 3: Безопасно кастуем birthyear через try_cast (если строка битая, вернется NULL)
    df_with_age = (
        df_valid
        .withColumn('birthyear_int', col('birthyear').try_cast('int'))
        .filter(col('birthyear_int').isNotNull())
        .withColumn('age', col('trip_year') - col('birthyear_int'))
        .filter((col('age') > 0) & (col('age') < 100)) # Отсекаем аномальный возраст
    )

    avg_duration_by_age = (
        df_with_age
        .groupBy('age')
        .agg(avg('tripduration').cast('double').alias('avg_tripduration'))
        .filter(col('age').isNotNull())
    )

    top_longest = (
        avg_duration_by_age
        .orderBy(desc('avg_tripduration'))
        .limit(10)
        .withColumn('trip_type', lit('longest'))
    )

    top_shortest = (
        avg_duration_by_age
        .orderBy(asc('avg_tripduration'))
        .limit(10)
        .withColumn('trip_type', lit('shortest'))
    )

    df_q6 = top_longest.unionByName(top_shortest)

    return df_q6