import pika
import uuid
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
    


class OcrRpcClient(object):
    """RPC-клиент для взаимодействия с OCR-сервисом через RabbitMQ.

    Использует механизм Remote Procedure Call (RPC) для отправки сообщений в очередь `ocr_service`
    и получения ответа через временную callback-очередь.

    Пример использования:
        >>> client = OcrRpcClient()
        >>> response = client.call({"image": "base64_encoded_image"})
    """

    def __init__(self):
        """Инициализирует подключение к RabbitMQ и настраивает callback-очередь для ответов."""
        # Подключение к RabbitMQ
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_URL)
        )
        self.channel = self.connection.channel()

        # Создаем временную очередь с уникальным именем для получения ответов
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        # Подписываемся на свою очередь, чтобы получать ответы
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True  # Автоматическое подтверждение получения сообщения
        )

        # Переменные для хранения ответа и корреляционного ID
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        """Callback-функция, вызываемая при получении ответа от сервера.

        Args:
            ch: Канал RabbitMQ.
            method: Метод доставки сообщения.
            props: Свойства сообщения (включая correlation_id).
            body: Тело сообщения (ответ от сервера).
        """
        # Проверяем, что ответ соответствует нашему запросу (по correlation_id)
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message):
        """Отправляет сообщение в OCR-сервис и ожидает ответа.

        Args:
            message (dict): Данные для обработки (например, изображение в base64).

        Returns:
            dict: Ответ от OCR-сервиса (распарсенный JSON).

        Пример:
            >>> client.call({"image": "base64_data"})
            {"text": "распознанный текст", "confidence": 0.95}
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())  # Генерируем уникальный ID запроса

        # Отправляем сообщение в очередь `ocr_service`
        self.channel.basic_publish(
            exchange='',
            routing_key='ocr_service',  # Имя очереди, куда отправляем запрос
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,  # Очередь для ответа
                correlation_id=self.corr_id,  # ID для сопоставления запроса и ответа
            ),
            body=json.dumps(message)  # Сериализуем сообщение в JSON
        )

        # Ожидаем ответа, проверяя входящие сообщения
        while self.response is None:
            self.connection.process_data_events()  # Неблокирующее ожидание

        # Десериализуем ответ и возвращаем
        return json.loads(self.response)