import pika
from app.config import RABBITMQ_URL

def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='gatewayservice')
    return connection, channel 