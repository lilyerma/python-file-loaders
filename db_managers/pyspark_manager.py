from pyspark.sql import SparkSession
from db_managers.base import BaseDBManager
from db_managers.db_factory import DBManagerFactory

class SparkManager(BaseDBManager):
    def __init__(self, spark_session: SparkSession = None, app_name: str = "PySparkApp"):
        self.spark = spark_session
        self.app_name = app_name

    def connect(self) -> SparkSession:
        # Если сессия еще не была передана, создаем новую
        if self.spark is None:
            self.spark = (
                SparkSession.builder
                .appName(self.app_name)
                .master("local[*]")
                .config("spark.driver.memory", "2g")
                .getOrCreate()
            )
            # Устанавливаем уровень логирования
            self.spark.sparkContext.setLogLevel("WARN")
            
        return self.spark

    def save_dataframe(self, df, table_name: str, mode: str = "append"):
        if self.spark is None:
            raise ValueError("Spark сессия не инициализирована. Сначала вызовите connect().")
        df.write.format("parquet").mode(mode).saveAsTable(table_name)

    def close(self):
        if self.spark:
            self.spark.stop()
            self.spark = None

DBManagerFactory.register("spark", SparkManager)