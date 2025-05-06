from .auth import auth_bp
from .user import user_bp
from .products import products_bp
from .analytics import analytics_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(analytics_bp)
