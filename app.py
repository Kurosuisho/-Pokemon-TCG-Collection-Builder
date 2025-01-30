from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash
from create_database import db, User


app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("Backend Project\data", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")

# Initialize Flask extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cors = CORS(app)


# auth routes
@app.route('/auth/register', methods=['POST'], strict_slashes=False)
def register():
    return jsonify({"message": "Register Test successful"})


@app.route('/auth/login', methods=['POST'])
def login():
    return jsonify({"message": "Login Test successful"})


@app.route('/auth/profile', methods=['GET'])
def profile():
    return jsonify({"message": "Profile Test successful"})



#cards routes
@app.route('/cards', methods=['POST'])
def cards():
    return jsonify({"message": "All Cards Test successful"})


@app.route('/cards/<int:cards_id>', methods=['POST'])
def card_id():
    return jsonify({"message": "Specific Cards Test successful"})



#collection routes
@app.route('/collection', methods=['POST'])
def collection():
    return jsonify({"message": "All Collections Test successful"})




if __name__ == "__main__":
    app.run(debug=True)