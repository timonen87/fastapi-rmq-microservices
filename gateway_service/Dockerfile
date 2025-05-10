FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY setup.py .
COPY app/ app/
RUN pip install --no-cache-dir -e .

# Копирование остальных файлов
COPY . .

# Открытие порта
EXPOSE 6001

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6001"] 