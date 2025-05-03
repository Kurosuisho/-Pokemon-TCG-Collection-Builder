
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from app.db import db
from app.config import Config
from app.models.user import User
from app.models.deck import Deck
from app.models.collection import Collection
from app.routes import register_routes
from app.routes.chat import chat_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["Authorization"], supports_credentials=True)
    limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])
    
    
    User.collections = db.relationship("Collection", back_populates="user", cascade="all, delete-orphan")
    User.decks = db.relationship("Deck", back_populates="user")
    
    # Register blueprints
    
    register_routes(app)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    swagger = Swagger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        }
    },
    "security": [{"Bearer": []}],
})
    
    @app.route('/')
    def index():
        return {"message": "Pokemon TCG Collection API"}
    

    return app