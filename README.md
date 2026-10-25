# 🚀 Python File Loaders & Processor

За основу данного приложения взяты практические упражнения из репозитория [Data Engineering Practice (Daniel Beach)](https://github.com/danielbeach/data-engineering-practice), на базе которых была спроектирована модульная архитектура, реализован паттерн **Template Method**, фабрика загрузчиков и гибкий CLI-интерфейс на паттерне **Плагинов/Авторегистрации (Plugin/Registry Pattern)**.

---

## 📚 Соответствие упражнениям курса и задачи проекта

Проект реализован пошагово. Подробное описание каждой задачи, принятых решений и обоснований вы найдете в документации:

1. **[Задача 1 (на основе Exercise 1): Базовый загрузчик и стратегии I/O](./docs/task_01_core_downloaders.md)**  
   * Пакетная загрузка файлов по HTTP и распаковка ZIP-архивов. Реализован шаблонный метод (`BaseFileDownloader` + `_prepare` + абстрактный `_fetch`), фабрика (`DownloaderFactory`), защита от *Path Traversal*, валидация и 4 стратегии загрузки (`thread`, `async`, `requests`, `wget`).
2. **[Задача 2 (на основе Exercise 2): Веб-скрапинг и пайплайн обработки](./docs/task_02_parser.md)**  
   * Веб-скрапинг, построение URI и последующая обработка данных.
3. **[Задача 3 (на основе Exercise 3): Потоковое чтение и облачный стриминг](./docs/task_03_line_reader.md)**  
   * Многошаговые сценарии работы с облачными источниками данных (в стиле AWS S3 / Common Crawl). Включает HTTP-стриминг в память (`BytesIO`), распаковку `.gz` «на лету», `LineReader` и профилирование памяти (`tracemalloc`).
4. **[Задача 4: Рекурсивный конвертер и флаттенинг JSON](./docs/task_04_parser.md)**
   * Обход вложенных (ragged) директорий с помощью `rglob`, разворачивание сложных вложенных структур данных в плоский формат (flattening) и пакетная конвертация в CSV.
5. **[Задача 5: Анализ данных, генерация DDL и миграции в PostgreSQL](./docs/task_05_csv_to_ddl.md)**
   * Рекурсивный анализ CSV-файлов (типы, null, min/max), автоматическая генерация схем `CREATE TABLE` с поименованными `PRIMARY KEY` и шаблонами `FOREIGN KEY`, управление подключением через SQLAlchemy и пакетный запуск миграций в цикле через изолированный Docker-контейнер с PostgreSQL.
6. **[Задача 6: Модульный PySpark Аналитический Пайплайн](./docs/task_06_pyspark.md)**
   * Распределенная обработка больших объемов транспортных данных (Divvy Trips) с использованием Apache Spark. Инкапсуляция логики ингестации архивов, динамический обход query-скриптов (`q1.py`–`q6.py`) с трекингом времени, обработка типов (`NaN`, `null`) и выгрузка результатов.
7. **[Задача 7: PySpark-пайплайн анализа жестких дисков (Backblaze)](./docs/task_07_pyspark.md)**
   * Чтение ZIP-архивов с CSV-данными «на лету» в оперативной памяти (без сохранения на диск через `sc.binaryFiles` и `zipfile`), выделение метаданных (`source_file`, `extracted_date`), парсинг бренда (`split`/`element_at`) и квантилирование емкости дисков по 5 квантилям (`ntile(5)` через вторичный датафрейм). Поддержка динамического запуска через CLI (`--query q7`).
8. **[Задача 8 (на основе Exercise 8): Аналитика, трансформации и Parquet-партиционирование на DuckDB](./docs/task_08_duckdb_parquet.md)**
   * Использование аналитического движка DuckDB для эффективного выполнения SQL-запросов и нативного экспорта витрин в формат **Apache Parquet с динамическим партиционированием** (`PARTITION_BY`). Выделение логики в изолированный класс `ParquetExporter` и CLI-команду `parquet-run`.

---

## 🗂 Структура проекта

```text
python-file-loaders/
├── commands/                # Изолированные модули CLI-команд (паттерн Плагинов с авторегистрацией)
│   ├── sql_run.py           # Пакетный запуск SQL-скриптов из папки
│   └── parquet_run.py       # Точечный экспорт SQL-запроса в Parquet с партициями
├── db_managers/             # Менеджеры баз данных (DuckDB, PostgreSQL, фабрика)
│   ├── base.py              # Абстрактный базовый класс БД
│   ├── db_factory.py        # Фабрика соединений с авторегистрацией
│   ├── duckdb_manager.py    # Менеджер DuckDB (транзакции, DataFrame, COPY)
│   ├── sql_runner.py        # Оркестратор папок со скриптами
│   └── parquet_exporter.py  # Выделенный сервис экспорта в Parquet
├── pyspark_task/            # Пакет аналитики на Apache Spark
├── downloader_pkg/          # Сетевые загрузчики
├── csv_to_pg_loader/        # Чтение csv и создание таблиц в PG (Exercise 5)
├── extractors/              # Модули распаковки архивов (ZIP / GZ)
├── readers/                 # Потоковая читалка (LineReader)
├── utils/                   # Профайлер памяти (tracemalloc)
├── docs/                    # Документация по задачам (включая task_08)
├── tests/                   # Набор unit-тестов (pytest)
├── new_cli.py               # Главная точка входа CLI (автообнаружение и регистрация команд)
├── json_flattening/         # Конвертер JSON в CSV
├── benchmark.py             # Скрипт бенчмарка загрузчиков
├── noaa_loader.py           # Парсер NOAA
├── experiment_s3.py         # Облачный стриминг-эксперимент
├── Dockerfile               # Инструкция сборки Docker-образа
├── docker-compose.yml       # Конфигурация сервисов
├── requirements.txt         # Зависимости проекта
└── README.md                # Главная документация
---

## ⚙️ Требования и установка (Локально)

> ⚠️ **Важно для PySpark:** Для работы пайплайна в системе (или в контейнере) должна быть установлена Java (JDK 11/17), так как Spark работает поверх JVM.

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
cd python-file-loaders
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запуск тестов:

```bash
python -m pytest
```

---

## 🐳 Запуск через Docker (Рекомендуется)

Проект полностью упакован для запуска в изолированной среде (с предустановленными Python и Java).

1. Соберите и запустите интерактивный контейнер:

```bash
docker compose run --rm downloader python -m pytest
```

---

## 🕹 Использование (`new_cli.py` и Авторегистрация)

Управление проектом осуществляется через единую точку входа **`new_cli.py`**. Архитектура построена по паттерну плагинов: при старте диспетчер автоматически сканирует папку `commands/`, собирает функции регистрации (`register_command`) и формирует CLI-интерфейс динамически.


* **Скачивание файлов:**
```bash
python new_cli.py download --method thread
```

* **Распаковка архивов (ZIP):**
```bash
python new_cli.py extract
```

* **Запуск бенчмарка скорости:**
```bash
python new_cli.py benchmark
```

* **Запуск облачного стриминг-эксперимента:**
```bash
python new_cli.py experiment
```

* **Запуск NOAA пайплайна (Парсинг + Загрузка + Анализ) (Task 2):**
```bash
python new_cli.py noaa --timestamp "2024-01-19 15:42"
```

* **Очистка временных файлов:**
```bash
python new_cli.py clean
```

* **Конвертация JSON в CSV с флаттенингом (Task 4):**
```bash
python new_cli.py convert --input ./data --output ./output_csv
```

* **Анализ CSV-файлов и вывод DDL-схемы (Task 5):**
```bash
python new_cli.py analyze --input csv_to_pg_loader/data
```

* **Пакетный запуск SQL-миграций в PostgreSQL (Task 5):**
```bash
python new_cli.py sql-run --dir csv_to_pg_loader/sql
```
* **Запуск модульного PySpark-пайплайна (Запросы Q1–Q6) (Task 6):**
```bash
python new_cli.py run-pyspark --zip pyspark_task/data/Divvy_Trips_2019_Q4.zip
```
* **Запуск конкретного PySpark запроса (Task 7):**
```bash
python new_cli.py run-pyspark --zip pyspark_task/data_7/hard-drive-2022-01-01-failures.csv.zip --query q7
```
* **Запуск конкретного SQL запроса и сохранение в Parquet (Task 8):**
```bash
python new_cli.py parquet-run -f duck_db/sql/q4.sql -o duck_db/output -p '"Model Year"'
```
* **Запуск конкретного папки с SQL запросами и сохранение в csv (Task 8):**
```bash
python new_cli.py sql-run -t duckdb -d duck_db/sql
```