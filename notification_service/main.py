import pika
import sys
import os
import time
import notification_service
from dotenv import load_dotenv


load_dotenv()
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")


def main():
    """Основная функция для обработки сообщений из RabbitMQ.

    Устанавливает соединение с RabbitMQ, объявляет очередь и начинает потребление сообщений.
    Каждое сообщение обрабатывается в callback-функции, где вызывается сервис уведомлений.
    В случае ошибки сообщение не подтверждается (NACK), при успехе — подтверждается (ACK).

    Raises:
        KeyboardInterrupt: Если пользователь прерывает выполнение (Ctrl+C).
        Exception: Любые другие ошибки при обработке сообщений логируются, но не прерывают работу.
    """
    # Подключение к RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        """Callback-функция, вызываемая при получении сообщения из очереди.

        Args:
            ch (Channel): Канал RabbitMQ.
            method (Method): Метод доставки сообщения.
            properties (Properties): Свойства сообщения.
            body (bytes): Тело сообщения (в бинарном виде).

        Обрабатывает сообщение через notification_service.
        - При успехе отправляет ACK (подтверждение).
        - При ошибке отправляет NACK (неподтверждение).
        """
        try:
            error = notification_service.send_notification_email(body)
            if error:
                ch.basic_nack(delivery_tag=method.delivery_tag)  # Не подтверждаем сообщение при ошибке
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем успешную обработку
        except Exception as e:
            print(f"Сообщение об ошибке при обработке: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)  # Отправляем NACK при исключении

    # Начинаем слушать очередь "email_notification"
    channel.basic_consume(queue="email_notification", on_message_callback=callback)

    print("Ждем сообщений. Для выхода нажмите CTRL+C")

    # Запускаем бесконечный цикл обработки сообщений
    channel.start_consuming()


if __name__ == "__main__":
    main()
