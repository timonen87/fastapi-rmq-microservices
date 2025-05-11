# FastAPI RabbitMQ Microservices

Проект представляет собой микросервисную архитектуру, построенную с использованием FastAPI и RabbitMQ. Система включает в себя несколько сервисов, взаимодействующих между собой через API и очереди сообщений.

## Архитектура

```
fastapi-rmq-microservices/
├── gateway_service/           # API Gateway сервис
│   ├── app/
│   │   ├── models/           # Pydantic модели
│   │   ├── routes/           # API маршруты
│   │   ├── services/         # Сервисные компоненты
│   │   ├── config.py         # Конфигурация
│   │   ├── dependencies.py   # Зависимости
│   │   └── main.py          # Основной файл приложения
│   └── setup.py             # Установка пакета
├── user_service/            # Сервис пользователей
├── ocr_service/             # Сервис OCR
├── notifciation_service/    # Сервис отправки ссообщений
└── docker-compose.yml       # Docker конфигурация
```

## Требования

- Python 3.11+
- Docker и Docker Compose
- RabbitMQ
- PostgreSQL (для user_service)

## Установка и настройка

### Локальная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd fastapi-rmq-microservices
```

2. **Создание виртуального окружения**
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate  # для Windows
```

3. **Настройка переменных окружения**
 
Скопировать содержимое `.env.example` в локальный файл `.env`


4. **Установка зависимостей для каждого сервиса**
```bash
# Gateway Service
cd gateway_service
pip install -r requirements.txt

# User Service
cd ../user_service
pip install -r requirements.txt

# OCR Service
cd ../ocr_service
pip install -r requirements.txt

# Notification Service
cd ../notification_service
pip install -r requirements.txt
```

5. **Запуск сервисов**
```bash
# Gateway Service
cd gateway_service
uvicorn app.main:app --host localhost --port 6001 --reload

# User Service
cd ../user_service
uvicorn main:app --host localhost --port 6000 --reload

# OCR Service
cd ../ocr_service
uvicorn main:app --host localhost --port 8001 --reload

# Notification Service
cd ../notification_service
python main.py
```

### Установка через Docker Compose

1. **Подготовка**
```bash
git clone <repository-url>
cd fastapi-rmq-microservices
```

2. **Настройка переменных окружения**
Создайте файл `.env` в корневой директории (как описано выше)

3. **Запуск всех сервисов**
```bash
docker-compose up --build
```

4. **Запуск отдельных сервисов**
```bash
# Запуск только необходимых сервисов
docker-compose up gateway_service user_service rabbitmq postgres
```

5. **Остановка сервисов**
```bash
docker-compose down
```

## Проверка работоспособности

1. **API Documentation**
- Swagger UI: `http://localhost:6001/docs`
- ReDoc: `http://localhost:6001/redoc`

2. **RabbitMQ Management**
- URL: `http://localhost:15672`
- Логин: guest
- Пароль: guest

3. **PostgreSQL**
- Хост: localhost
- Порт: 5432
- База данных: userdb
- Пользователь: postgres
- Пароль: postgres

## API Endpoints

### Gateway Service (Port 6001)

#### Аутентификация
- `POST /auth/login` - Вход в систему
- `POST /auth/register` - Регистрация
- `POST /auth/generate_otp` - Генерация OTP
- `POST /auth/verify_otp` - Проверка OTP

#### OCR Service
- `POST /ocr` - Обработка изображения

### User Service (Port 6000)
- `POST /api/token` - Получение JWT токена
- `POST /api/users` - Создание пользователя
- `POST /api/users/generate_otp` - Генерация OTP
- `POST /api/users/verify_otp` - Проверка OTP

## Разработка

### Добавление нового сервиса

1. Создайте новую директорию для сервиса
2. Добавьте необходимые файлы (main.py, requirements.txt, Dockerfile)
3. Обновите docker-compose.yml
4. Добавьте сервис в сеть app-network


## Безопасность

- Все пароли хешируются
- JWT для аутентификации
- CORS защита
- Чувствительные данные в переменных окружения
- Rate limiting на уровне Gateway
- Валидация входных данных через Pydantic

## Мониторинг и логирование

- Логи доступны через Docker Compose: `docker-compose logs -f`

