from flask_session import Session
import redis
from kafka import KafkaProducer
import mysql.connector
import json

class MySQL:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def init_app(self, app):
        self.conn = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        self.cursor = self.conn.cursor(dictionary=True)

db = MySQL()

class RedisStore:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        self.client = redis.Redis(
            host=app.config['SESSION_REDIS_HOST'],
            port=app.config['SESSION_REDIS_PORT'],
            decode_responses=True
        )

r = RedisStore()

class KafkaProducerWrapper:
    def __init__(self):
        self.producer = None

    def init_app(self, app):
        self.producer = KafkaProducer(
            bootstrap_servers=app.config['KAFKA_BROKER'],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

kafka_producer = KafkaProducerWrapper()

sess = Session()
