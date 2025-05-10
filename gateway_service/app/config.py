from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Environment variables
SECRET_KEY = os.environ.get("SECRET_KEY")
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

# CORS settings
CORS_ORIGINS = os.environ.get("CORS_ORIGINS")
CORS_CREDENTIALS = os.environ.get("CORS_CREDENTIALS")
CORS_METHODS = os.environ.get("CORS_METHODS")
CORS_HEADERS = os.environ.get("CORS_HEADERS")