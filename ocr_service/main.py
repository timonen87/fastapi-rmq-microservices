import pika
import json
from service import OCRService, send_notification_email
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
nRABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue='ocr_service')

# Callback function to process OCR requests
def ocr_request(ch, method, props, body):
    ocr_service = OCRService()
    try:
        # Process OCR request
        response = ocr_service.process_request(body)

        # Send email notification
        send_notification_email(response['user_email'], response['ocr_text'], channel)

        # Publish response to the reply queue
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response)
        )
        print(f"Ошибка при отправке запроса user_id: {response['user_id']}")
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
    finally:
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Set prefetch count to 1 and start consuming
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ocr_service', on_message_callback=ocr_request)

print("Ожидание RPC запросов")
channel.start_consuming()
