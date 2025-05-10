FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY . .

# Открытие порта
# EXPOSE 8002

# Запуск приложения
# CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8002"] 