# 🚀 Python File Loaders & Processor

За основу данного приложения взяты практические упражнения из репозитория [Data Engineering Practice (Daniel Beach)](https://github.com/danielbeach/data-engineering-practice), на базе которых была спроектирована собственная модульная архитектура, добавлены продвинутые стратегии параллелизма, потоковая обработка и CLI-интерфейс.

---

## 📚 Соответствие упражнениям курса и задачи проекта

Проект реализован пошагово. Подробное описание каждой задачи, принятых решений и обоснований вы найдете в документации:

1. **[Задача 1 (на основе Exercise 1): Базовый загрузчик и стратегии I/O](./docs/task_01_core_downloaders.md)**  
   * Пакетная загрузка файлов по HTTP и распаковка ZIP-архивов. Реализован шаблонный метод (`BaseFileDownloader`), защита от *Path Traversal*, валидация и 4 стратегии загрузки (`thread`, `async`, `requests`, `wget`).
2. **[Задача 2 (на основе Exercise 2): Веб-скрапинг и пайплайн обработки](./docs/task_02_parser.md)**  
   * Веб-скрапинг, построение URI и последующая обработка данных.
3. **[Задача 3 (на основе Exercise 3): Потоковое чтение и облачный стриминг](./docs/task_03_line_reader.md)**  
   * Многошаговые сценарии работы с облачными источниками данных (в стиле AWS S3 / Common Crawl). Включает HTTP-стриминг в память (`BytesIO`), распаковку `.gz` «на лету», `LineReader` и профилирование памяти (`tracemalloc`).
4. **[Задача 4: Рекурсивный конвертер и флаттенинг JSON](docs/task_04_parser.md)**
   * Обход вложенных (ragged) директорий с помощью rglob, разворачивание сложных вложенных структур данных в плоский формат (flattening) и пакетная конвертация в CSV.
5. **[Задача 5: Анализ данных, генерация DDL и миграции в PostgreSQL](./docs/task_05_csv_to_ddl.md)**
    * Рекурсивный анализ CSV-файлов (типы, null, min/max), автоматическая генерация схем CREATE TABLE с поименованными PRIMARY KEY и шаблонами FOREIGN KEY, управление подключением через SQLAlchemy и пакетный запуск миграций в цикле через изолированный Docker-контейнер с PostgreSQL.

---

## 🗂 Структура проекта

```text
python-file-loaders/
├── csv_to_pg_loader/        # Чтение csv и создание таблиц в PG (Exercise 5)
├── downloader_pkg/          # Сетевые загрузчики (Часть Exercise 1) 
├── extractors/              # Модули распаковки архивов (ZIP / GZ) (Часть Exercise 1 и 3)
├── readers/                 # Потоковая читалка (LineReader) (Часть Exercise 2)
├── utils/                   # Профайлер памяти (tracemalloc) (Допом к Exercise 2)
├── docs/                    # Документация по задачам 
├── tests/                   # Набор unit-тестов (pytest)
├── cli.py                   # Главный CLI-интерфейс управления
├── json_flattening/         # Поиск json фалов и приведение к плоскому csv (Exercise 4)
├── benchmark.py             # Скрипт сравнения времени загрузки разнымии loader-ами (Exercise 1)
├── noaa_loader.py           # Парсер сайта noaa (Exercise 2)
├── experiment_s3.py         # Скрипт облачного стриминг-эксперимента (Exercise 3)
├── Dockerfile               # Инструкция сборки Docker-образа
├── docker-compose.yml       # Конфигурация сервисов Docker
├── requirements.txt         # Зависимости проекта
└── README.md                # Главная документация
```

---

## ⚙️ Требования и установка (Локально)

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

Проект полностью упакован для запуска в изолированной среде.

1. Соберите и запустите интерактивный контейнер:
```bash
docker compose run --rm downloader python -m pytest
```

---

## 🕹 Использование (CLI Команды)

Приложение управляется через `cli.py`:

* **Скачивание файлов:**
  ```bash
  python cli.py download --method thread
  ```
* **Распаковка архивов (ZIP):**
  ```bash
  python cli.py extract
  ```
* **Запуск бенчмарка скорости:**
  ```bash
  python cli.py benchmark
  ```
* **Запуск облачного стриминг-эксперимента:**
  ```bash
  python cli.py experiment
  ```
* **Запуск NOAA пайплайна (Парсинг + Загрузка + Анализ) (Task 2):**
  ```bash
  python cli.py noaa

* **Очистка временных файлов:**
  ```bash
  python cli.py clean

* **Конвертация JSON в CSV с флаттенингом (Task 4):**
  ```bash
  python cli.py convert --input ./data --output ./output_csv

* **Анализ CSV-файлов и вывод DDL-схемы (Task 5):**
  ```bash
  python cli.py analyze --input csv_to_pg_loader/data

* **Пакетный запуск SQL-миграций в PostgreSQL (Task 5):**

  ```bash
  python cli.py run-sql --dir csv_to_pg_loader/sql