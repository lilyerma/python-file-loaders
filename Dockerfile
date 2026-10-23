FROM python:3.10-slim

WORKDIR /app

# 1. Устанавливаем системные зависимости (Java), которые меняются редко
RUN apt-get update && apt-get install -y default-jdk \
    && rm -rf /var/lib/apt/lists/*

# 2. Копируем только requirements.txt, чтобы кэшировать установку пакетов Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Копируем весь остальной код приложения в последнюю очередь
COPY . .