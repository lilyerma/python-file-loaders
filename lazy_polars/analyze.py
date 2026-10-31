import polars as pl

schema = {
    # Идентификаторы и текстовые категории со строгой длиной
    "ride_id": pl.Utf8,
    "rideable_type": pl.Categorical,  # Категориальный тип (ограниченный набор видов велосипедов)
    
    # Временные метки (парсятся как Datetime или Utf8 с последующим to_datetime)
    "started_at": pl.Datetime,
    "ended_at": pl.Datetime,
    
    # Текстовые поля станций с пропусками (Nulls)
    "start_station_name": pl.Utf8,
    "start_station_id": pl.Utf8,
    "end_station_name": pl.Utf8,
    "end_station_id": pl.Utf8,
    
    # Координаты (широта и долгота)
    "start_lat": pl.Float64,
    "start_lng": pl.Float64,
    "end_lat": pl.Float64,
    "end_lng": pl.Float64,
    
    # Тип пользователя ('member' или 'casual')
    "member_casual": pl.Categorical
}

# 1. Считываем данные в LazyFrame
df = pl.scan_csv(
    "lazy_polars/data/202306-divvy-tripdata.csv",
    schema=schema,
    try_parse_dates=True  # Автоматический парсинг строк YYYY-MM-DD HH:MM:SS в Datetime
)

# 2. Группируем по датам
grouped_by_date = (
    df.with_columns(
        date=pl.col("started_at").dt.date()
    )
    .group_by("date")
    .agg(ride_count=pl.col("ride_id").count())
    .sort("date")
)

# 3. Добавляем календарные признаки
week_and_days = grouped_by_date.with_columns(
    weekday=pl.col("date").dt.weekday(),
    week=pl.col("date").dt.week()
)

# 4. Формируем сдвиг недели (+1) для JOIN по полю "weekday" 
week_and_days_prev = week_and_days.select(
    "weekday", 
    week=pl.col("week") + 1,
    ride_count_prev=pl.col("ride_count")
)

# 5. Джойним, считаем разницу и выполняет вычисления (.collect())
result = (
    week_and_days
    .join(
        week_and_days_prev,
        on=["weekday", "week"],
        how="left"
    )
    .with_columns(
        diff=pl.col("ride_count").cast(pl.Int64) - pl.col("ride_count_prev").cast(pl.Int64)
    )
    .sort("date")
    .collect() 
)

print("--- Сравнение дней с предыдущей неделей ---")
print(result.head(10))

# 6. Статистика по неделям с выполнением вычислений
week_stats = (
    grouped_by_date
    .with_columns(week=pl.col("date").dt.week())
    .group_by("week")
    .agg(weekly_rides=pl.col("ride_count").sum())
    .select(
        max_weekly_rides=pl.col("weekly_rides").max(),
        min_weekly_rides=pl.col("weekly_rides").min(),
        avg_weekly_rides=pl.col("weekly_rides").mean()
    )
    .collect()  # <-- Запускает выполнение плана
)

print("\n--- Агрегированная статистика по всем неделям ---")
print(week_stats)