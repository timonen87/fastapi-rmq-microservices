import jwt
from sqlalchemy.orm import Session
import email_validator as _email_check
from fastapi import Depends, HTTPException, security

import fastapi.security as _security
from db.session import SessionLocal, get_db
from passlib.hash import bcrypt
from db.session import Base, SessionLocal, engine, settings
from models.user_model import User
from schemas.user_schema import UserCreate, UserSchema
import random
import json
import pika
import time
import os


connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue='email_notification')


def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))


def connect_to_rabbitmq():
    # Connect to RabbitMQ
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(settings.RABBITMQ_URL)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(
                "Не удалось подключиться к RabbitMQ. Повторная попытка через 5 секунд..."
            )
            time.sleep(5)


def send_otp(email, otp, channel):
    # Send an OTP email notification using RabbitMQ
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    message = {
        "email":email,
        "subject": "Уведомление OTP о верификации учетной записи",
        "other": "null",
        "body": f"Ваш OTP для верификации учетной записи: {otp} \n Пожалуйста, введите этот OTP на странице верификации, чтобы завершить настройку учетной записи. \n Если вы не запрашивали этот OTP, пожалуйста, проигнорируйте это сообщение.\n Благодарю вас ",
    }

    try:
        queue_declare_ok = channel.queue_declare(
            queue="email_notification", passive=True
        )
        current_durable = queue_declare_ok.method.queue

        if current_durable:
            if queue_declare_ok.method.queue != current_durable:
                channel.queue_delete(queue="email_notification")
                channel.queue_declare(queue="email_notification", durable=True)
        else:
            channel.queue_declare(queue="email_notification", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="email_notification",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print("Sent OTP email notification")
    except Exception as err:
        print(f"Failed to publish message: {err}")
    finally:
        channel.close()
        connection.close()
