from flask import Blueprint, request, session, jsonify
from extensions import kafka_producer , r , db
from datetime import datetime
import json
from routes.products import products_bp 
analytics_bp = Blueprint('analytics', __name__, url_prefix='')

from cassandra.cluster import Cluster
from flask import Blueprint, jsonify

# Assuming the Cassandra connection is setup correctly
cluster = Cluster(['127.0.0.1'])  # Point to your Cassandra cluster
cassandra_session  = cluster.connect('ecommerce')  # 'ecommerce' is your Cassandra keyspace

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/jsonrecommended', methods=['GET'])
def get_recommended_products():
    # Try to get cached recommendations from Redis
    cached_recommendations = r.client.get('recommended_products')

    if cached_recommendations:
        print("Using Redis cache for recommended products.")
        print(cached_recommendations)
        return jsonify(json.loads(cached_recommendations))
    
    # If cache is empty, fetch from Cassandra
    query = "SELECT * FROM user_recommendations"
    rows = cassandra_session.execute(query)
    recommendations = []
    for row in rows:
        recommendations.append({
            'user_id': row.user_id,
            'recommended_items': row.recommended_items
        })

    # Cache the recommendations in Redis for 300 seconds (5 minutes)
    r.client.set('recommended_products', json.dumps(recommendations), ex=300)

    return jsonify(recommendations)








@analytics_bp.route('/log_interaction', methods=['POST'])
def log_interaction():
    data = request.get_json()
    print("Received request data:", data)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required_fields = ['product_id', 'action']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    if 'user_id' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    interaction_data = {
        "product_id": int(data['product_id']),
        "user_id": session['user_id'],
        "action": data['action'],
        "category": data.get('category', 'Unknown'),
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"Sending interaction data to Kafka: {interaction_data}")

    try:
        kafka_producer.producer.send("user_interactions", value=interaction_data)
    except Exception as e:
        print(f"Kafka error: {e}")

    return jsonify({"message": "Interaction logged successfully"}), 200

@analytics_bp.route('/log_filter_interaction', methods=['POST'])
def log_filter_interaction():
    data = request.get_json()
    print("Received filter interaction:", data)

    if not data or 'action' not in data:
        return jsonify({"error": "Missing required filter interaction fields"}), 400

    interaction_data = {
        "user_id":  session['user_id'],
        "category": data.get('category', 'filter'),
        "brands": data.get('brands','filter'),
        "min_price": data.get('min_price',''),
        "max_price": data.get('max_price',''),
        "rating": data.get('rating',''),
        "timestamp": datetime.utcnow().isoformat()
    }

    print("Sending filter interaction to Kafka:", interaction_data)
    try:
        kafka_producer.producer.send("filter_interactions", value=interaction_data)
    except Exception as e:
        print(f"Kafka error: {e}")
    return jsonify({"message": "Filter interaction logged successfully"}), 200

@analytics_bp.route('/log_search_interaction', methods=['POST'])
def log_search_interaction():
    data = request.get_json()
    print("Received search interaction:", data)

    if not data or 'action' not in data:
        return jsonify({"error": "Missing required search interaction fields"}), 400

    interaction_data = {
        "user_id":  session['user_id'],
        "value": data['value'],
        "session_ID": data["session_id"],
        "timestamp": datetime.utcnow().isoformat()
    }

    print("Sending filter interaction to Kafka:", interaction_data)
    try:
        kafka_producer.producer.send("search_interactions", value=interaction_data)
    except Exception as e:
        print(f"Kafka error: {e}")
    return jsonify({"message": "Filter interaction logged successfully"}), 200

@analytics_bp.route('/log_session_start', methods=['POST'])
def log_session_start():
    data = request.get_json()
    try:
        kafka_producer.producer.send("user_session_time", {
            "user_id": data["user_id"],
            "session_id": session["session_id"],
            "start_time": data["start_time"],
            "end_time": None,
            "duration_seconds": None
        })
    except Exception as e:
        print(f"Kafka error: {e}")
    return jsonify({"message": "Session start logged"}), 200

@analytics_bp.route('/log_session_end', methods=['POST'])
def log_session_end():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("Failed to parse JSON:", e)
        return jsonify({"error": "Invalid request body"}), 400

    try:
        kafka_producer.producer.send("user_session_time", {
            "user_id": data["user_id"],
            "session_id": data["session_id"],
            "end_time": data["end_time"]
        })
    except Exception as e:
        print(f"Kafka error: {e}")
    return jsonify({"message": "Session end logged"}), 200