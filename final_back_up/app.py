from flask import Flask
from config import Config
from extensions import db, r, kafka_producer, sess 
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    r.init_app(app)
    kafka_producer.init_app(app)
    sess.init_app(app)
    # Register routes
    register_routes(app)

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
