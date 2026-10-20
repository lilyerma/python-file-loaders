"""Модуль для работы с климатическими данными NOAA NCEI.

Включает:
1. Парсер для поиска ссылки по таймстампу.
2. Использование существующего RequestsFileDownloader.
3. Модуль чтения и записи DataFrame (pandas).
4. Анализатор для поиска максимума HourlyDryBulbTemperature.
"""

import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Импортируем готовый загрузчик из структуры проекта
from downloader_pkg import RequestsFileDownloader


class NoaaParser:
  """1. Парсер: поиск ссылки на файл по таймстампу в каталоге NOAA."""

  def __init__(self, base_url: str):
    self.base_url = base_url

  def find_file_url(self, target_timestamp: str) -> str:
    print(
        f"Подключаемся к каталогу NOAA: {self.base_url} (сервер может отвечать"
        " медленно)..."
    )
    try:
      response = requests.get(self.base_url, timeout=30)
      response.raise_for_status()
    except requests.exceptions.RequestException as e:
      raise ConnectionError(f"Ошибка при запросе страницы NOAA: {e}")

    soup = BeautifulSoup(response.text, "html.parser")
    target_href = None

    for row in soup.find_all("tr"):
      cols = row.find_all("td")
      if len(cols) >= 2:
        timestamp_text = cols[1].get_text(strip=True)
        if target_timestamp in timestamp_text:
          link_tag = cols[0].find("a")
          if link_tag and link_tag.has_attr("href"):
            target_href = link_tag["href"]
            break

    if not target_href:
      raise ValueError(
          f"Файл с таймстампом '{target_timestamp}' не найден на странице."
      )

    return urljoin(self.base_url, target_href)


class NoaaDataFrameHandler:
  """3. Модуль чтения и записи данных в DataFrame (pandas)."""

  @staticmethod
  def read_csv_to_df(file_path: str) -> pd.DataFrame:
    """Читает CSV-файл климатических данных в pandas DataFrame."""
    print(f"📖 Читаем файл в DataFrame: {file_path}")
    if not os.path.exists(file_path):
      raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    # low_memory=False отключает предупреждения о смешанных типах в больших CSV
    df = pd.read_csv(file_path, low_memory=False)
    print(f"✅ Данные успешно загружены. Строк: {len(df)}, Колонок: {len(df.columns)}")
    return df

  @staticmethod
  def save_df_to_csv(df: pd.DataFrame, output_path: str):
    """Сохраняет DataFrame обратно в CSV."""
    df.to_csv(output_path, index=False)
    print(f"💾 DataFrame успешно сохранен в: {output_path}")


class NoaaAnalyzer:
  """4. Модуль анализа климатических данных."""

  @staticmethod
  def get_max_dry_bulb_temperature(df: pd.DataFrame) -> float:
    """Находит максимальное значение параметра HourlyDryBulbTemperature."""
    target_column = "HourlyDryBulbTemperature"
    
    if target_column not in df.columns:
      raise ValueError(f"Колонка '{target_column}' отсутствует в данном датасете.")

    # Приводим к числовому типу, заменяя артефакты/текст (например, 's', пробелы) на NaN
    temp_series = pd.to_numeric(df[target_column], errors="coerce")
    
    max_val = temp_series.max()
    print(f"📈 Максимальное значение {target_column}: {max_val}")
    return max_val


class NoaaPipeline:
  """Оркестратор: связывает все шаги пайплайна воедино."""

  DEFAULT_URL = (
      "https://www.ncei.noaa.gov/data/local-climatological-data/access/2021/"
  )

  def __init__(self, base_url: str = DEFAULT_URL, output_dir: str = "./downloads"):
    self.base_url = base_url
    self.output_dir = output_dir
    os.makedirs(self.output_dir, exist_ok=True)

    self.parser = NoaaParser(base_url)
    self.data_handler = NoaaDataFrameHandler()
    self.analyzer = NoaaAnalyzer()

  def run(self, target_timestamp: str):
    """Запускает полный цикл: поиск -> загрузка существующим методом -> чтение -> анализ."""
    # Шаг 1: Парсинг ссылки
    file_url = self.parser.find_file_url(target_timestamp)
    filename = os.path.basename(file_url)
    print(f"🔍 Найден файл: {filename} -> {file_url}")

    # Шаг 2: Использование существующего загрузчика (RequestsFileDownloader)
    print(f"🚀 Запускаем скачивание через RequestsFileDownloader...")
    downloader = RequestsFileDownloader(urls=[file_url], output_dir=self.output_dir)
    downloader.download_all()

    file_path = os.path.join(self.output_dir, filename)

    # Шаг 3: Чтение в DataFrame
    df = self.data_handler.read_csv_to_df(file_path)

    # Шаг 4: Анализ данных (максимум температуры)
    max_temp = self.analyzer.get_max_dry_bulb_temperature(df)

    return max_temp