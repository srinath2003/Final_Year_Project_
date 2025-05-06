from kafka import KafkaConsumer
from cassandra.cluster import Cluster
import json
from datetime import datetime
import threading
from uuid import UUID

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'])  # Replace with your Cassandra node IP
session_cassandra = cluster.connect('ecommerce')

# Kafka Consumer Configuration
KAFKA_TOPIC = "user_interactions"
KAFKA_BROKER = "172.22.213.208:9092"

# Topics
TOPIC_LIKE = "like_interactions"
TOPIC_ADD_TO_CART = "add_to_cart_interactions"
TOPIC_VIEW_DETAILS = "view_details_interactions"

#Session Topic
TOPIC_SESSION = "user_session_time"
#Filter Topic
TOPIC_FILTER = "filter_interactions"
TOPIC_SEARCH = "search_interactions"
# Cache for tracking session start times
session_cache = {}
# Initialize Consumer -  same topic
# consumer = KafkaConsumer(
#     KAFKA_TOPIC,
#     bootstrap_servers=KAFKA_BROKER,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8"))
# )


# ###  Initialize Consumer - seperate topics
# consumer = KafkaConsumer(
#     TOPIC_LIKE,
#     TOPIC_ADD_TO_CART,
#     TOPIC_VIEW_DETAILS,
#     bootstrap_servers=KAFKA_BROKER,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8"))
# )


# Define Consumer Functions
def consume_user_interactions():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer:
        data = message.value
        print(f"User Interaction Received: {data}")
        session_cassandra.execute("""
            INSERT INTO user_interactions1 (user_id, action_timestamp, action, category, product_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["user_id"],
            datetime.fromisoformat(data["timestamp"]),
            data["action"],
            data.get("category", "N/A"),
            data.get("product_id", None)
        ))
        print("User Interaction inserted into Cassandra.")

def consume_filter_interactions():
    consumer_filter = KafkaConsumer(
        TOPIC_FILTER,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer_filter:
        data = message.value
        print(f"Filter Interaction Received: {data}")
        session_cassandra.execute("""
            INSERT INTO user_filter_interactions (user_id,timestamp, brands, category, max_price , min_price , rating)
            VALUES (%s,%s, %s, %s, %s,%s, %s)
        """, (
            data["user_id"],
            #data["session_id"],
            datetime.fromisoformat(data["timestamp"]),
            data["brands"],
            data["category"],
            data["max_price"],
            data["min_price"],
            data["rating"]

        ))
        print("Filter Interaction inserted into Cassandra.")

def consume_search_interactions():
    consumer_filter = KafkaConsumer(
        TOPIC_SEARCH,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer_filter:
        data = message.value
        print(f"Search Interaction Received: {data}")
        try:
            session_cassandra.execute("""
            INSERT INTO user_search_interactions (user_id,timestamp, session_id, value)
            VALUES (%s,%s, %s, %s)
        """, (
            data["user_id"],
            datetime.fromisoformat(data["timestamp"]),
            UUID(data["session_ID"]),
            data["value"]
        ))
        except Exception as e:
            print(e)
        print("Search Interaction inserted into Cassandra.")

def consume_session_time():
    consumer = KafkaConsumer(
        TOPIC_SESSION,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer:
        data = message.value
        session_id = data["session_id"]
        user_id = data["user_id"]

        print(f"[user_session_time] Received: {data}")

        if data.get("start_time") and not data.get("end_time"):
            # New session started
            session_cache[session_id] = data["start_time"]
            session_cassandra.execute("""
                INSERT INTO user_session_time (user_id, session_id, start_time)
                VALUES (%s, %s, %s)
            """, (
                user_id,
                session_id,
                datetime.fromisoformat(data["start_time"])
            ))
            print("[user_session_time] Start logged.")
        
        elif data.get("end_time"):
            start_time = session_cache.get(session_id)
            end_time = data["end_time"]
            if start_time:
                duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).seconds
                session_cassandra.execute("""
                    UPDATE user_session_time
                    SET end_time=%s, duration_seconds=%s
                    WHERE session_id=%s
                """, (
                    datetime.fromisoformat(end_time),
                    duration,
                    session_id
                ))
                print("[user_session_time] End + Duration updated.")

# ## New logic to avoid duplicate records
# def consume_session_time():
#     consumer = KafkaConsumer(
#         TOPIC_SESSION,
#         bootstrap_servers=KAFKA_BROKER,
#         value_deserializer=lambda m: json.loads(m.decode("utf-8"))
#     )
#     for message in consumer:
#         data = message.value
#         session_id = data["session_id"]
#         user_id = data["user_id"]

#         print(f"[user_session_time] Received: {data}")

#         start_time = data.get("start_time")
#         end_time = data.get("end_time")
#         duration = data.get("duration_seconds")

#         if start_time and not end_time:
#             # New session started
#             session_cache[session_id] = start_time
#             session_cassandra.execute("""
#                 INSERT INTO user_session_time (user_id, session_id, start_time)
#                 VALUES (%s, %s, %s)
#             """, (
#                 user_id,
#                 session_id,
#                 datetime.fromisoformat(start_time)
#             ))
#             print("[user_session_time] Start logged.")

#         elif end_time:
#             # End session and update duration
#             if not start_time:
#                 # Try to get start_time from cache if not provided
#                 start_time = session_cache.get(session_id)

#             session_cassandra.execute("""
#                 UPDATE user_session_time
#                 SET end_time = %s,
#                     duration_seconds = %s
#                 WHERE session_id = %s
#             """, (
#                 datetime.fromisoformat(end_time),
#                 duration if duration is not None else (
#                     (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).seconds
#                     if start_time else None
#                 ),
#                 session_id
#             ))
#             print("[user_session_time] End + Duration updated.")

# Start Threads
print("Kafka Consumers started...")

t1 = threading.Thread(target=consume_user_interactions)
t2 = threading.Thread(target=consume_filter_interactions)
t3 = threading.Thread(target=consume_session_time) 
t4 = threading.Thread(target=consume_search_interactions)
t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()