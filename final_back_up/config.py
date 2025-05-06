import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")
    SESSION_TYPE = 'redis'
    SESSION_REDIS_HOST = 'localhost'
    SESSION_REDIS_PORT = 6379
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 600
    SESSION_REFRESH_EACH_REQUEST = False

    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    KAFKA_BROKER = "172.22.213.208:9092"
    KAFKA_TOPICS = {
        "main": "user_interactions",
        "like": "like_interactions",
        "view_details": "view_details_interactions",
        "add_to_cart": "add_to_cart_interactions",
        "filter": "filter_interactions",
        "session": "user_session_time"
    }
