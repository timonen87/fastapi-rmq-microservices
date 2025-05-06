
from fastapi import FastAPI
from api.route import router_users
from core.config import settings
from db.session import engine, Base
import logging
import pika
# from models.user_model import Base

# rabbitmq connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue='email_notification')


app = FastAPI(
    title=settings.PROJENCT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(engine)

app.include_router(router_users)

@app.get("/hello")
async def root():
    return {"message": "Hello World"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", reload=True, port=6000)