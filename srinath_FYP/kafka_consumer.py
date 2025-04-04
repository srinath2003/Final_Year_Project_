from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import json
from datetime import datetime

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'])  # Replace with your Cassandra node IP
session_cassandra = cluster.connect('ecommerce')

# Kafka Consumer Configuration
KAFKA_TOPIC = "user_interactions"
KAFKA_BROKER = "172.22.213.208:9092"

# Initialize Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Kafka Consumer started... Waiting for messages.")

# Read messages and insert into Cassandra
for message in consumer:
    data = message.value
    print(f"Received from Kafka: {data}")

    session_cassandra.execute("""
        INSERT INTO user_interactions1 (user_id, action_timestamp, action, category, product_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (data["user_id"], datetime.fromisoformat(data["timestamp"]), data["action"], 
          data["category"], data["product_id"]))

    print("Data inserted into Cassandra.")
