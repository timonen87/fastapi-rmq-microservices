import json
import base64
import easyocr 
import pika
import os
from dotenv import load_dotenv
from typing import Dict, Any


load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")


class OCRService:
    """
    Сервис для распознавания текста на изображениях с использованием EasyOCR.
    Поддерживает английский и русский языки.
    """

    def __init__(self):
        """
        Инициализация OCR сервиса с поддержкой английского и русского языков.
        """
        self.reader = easyocr.Reader(['en', 'ru'])

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Извлекает текст из изображения с помощью EasyOCR.

        Args:
            image_path (str): Путь к изображению для обработки

        Returns:
            str: Распознанный текст, объединенный в одну строку
        """
        recognized_texts = self.reader.readtext(image_path)
        extracted_texts = [text[1] for text in recognized_texts]
        return ' '.join(extracted_texts)
    
    

    def process_ocr_request(self, message: str) -> Dict[str, Any]:
        """
        Обрабатывает входящий запрос на распознавание текста.

        Args:
            message (str): JSON строка, содержащая данные запроса:
                - user_name: имя пользователя
                - user_email: email пользователя
                - user_id: ID пользователя
                - file: base64-encoded изображение

        Returns:
            Dict[str, Any]: Словарь с результатами обработки:
                - user_id: ID пользователя
                - user_name: имя пользователя
                - user_email: email пользователя
                - ocr_text: распознанный текст
        """
        request_data = json.loads(message)
        user_name = request_data['user_name']
        user_email = request_data['user_email']
        user_id = request_data['user_id']
        encoded_image = request_data['file']

        print(f"Processing OCR request for user_id: {user_id}")
        print(f"Request received from user: {user_name}")

        # Декодируем и сохраняем изображение
        image_data = base64.b64decode(encoded_image.encode())
        os.makedirs("data", exist_ok=True)
        image_path = "data/decoded_file.png"
        
        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)

        # Выполняем распознавание текста
        recognized_text = self.extract_text_from_image(image_path)
        print("Text recognition completed successfully")

        return {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "ocr_text": recognized_text
        }


def send_notification_email(email: str, ocr_text: str, channel: pika.channel.Channel) -> None:
    """
    Отправляет email уведомление о завершении распознавания текста.

    Args:
        email (str): Email адрес получателя
        ocr_text (str): Распознанный текст
        channel (pika.channel.Channel): Канал RabbitMQ для отправки сообщения

    Raises:
        Exception: При ошибке отправки сообщения в очередь
    """

    notification_message = {
        'email': email,
        'subject': 'Text Recognition Completed',
        'body': f'Text recognition has been completed. Recognized text: {ocr_text}',
        'other': None,
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key='email_notification',
            body=json.dumps(notification_message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print("Email notification sent successfully")
    except Exception as error:
        print(f"Failed to send notification message: {error}")