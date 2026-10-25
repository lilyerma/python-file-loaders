import os
from pathlib import Path

# Базовый путь проекта
BASE_DIR = Path(__file__).resolve().parent

# --- Настройки путей для файлов и архивов ---
DEFAULT_ZIP_PATH = BASE_DIR / "pyspark_task" / "data_7"
DEFAULT_TEMP_DIR = BASE_DIR / "temp_extracted"
RESULTS_DIR = BASE_DIR / "results"

# --- Настройки подключений к базам данных ---
# Для DuckDB (путь к файлу базы)
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(BASE_DIR / "analytics.duckdb"))

# Для PostgreSQL (строка подключения / URL)
POSTGRES_URL = os.getenv(
    "POSTGRES_URL", 
    "postgresql+psycopg2://postgres:secretpassword@postgres:5432/loader_db"
)

# Для Spark
SPARK_APP_NAME = "DivvyPySparkCLI"
SPARK_MASTER = "local[*]"