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
    try:
        # Extract JSON data from request
        data = request.get_json()

        # Validate required fields
        required_fields = {"username", "email", "password"}
        if not data or not required_fields.issubset(data):
            return jsonify({"error": "Missing username, email, or password"}), 400

        username = data["username"]
        email = data["email"]
        password = data["password"]

        # Check if username or email is already taken
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 409

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user instance
        new_user = User(username=username, email=email, password_hash=hashed_password)

        # Save user to database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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