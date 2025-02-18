from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from dotenv import load_dotenv
import os
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from create_database import db, User

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Thisisatest25!@localhost:5432/Project Database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cors = CORS(app)

@app.route('/auth/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    if request.method == 'GET':
        return render_template("register.html")  # Show form before submission

    try:
        # Extract form data instead of JSON
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate required fields
        if not username or not email or not password:
            return jsonify({"error": "Missing username, email, or password"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user instance
        new_user = User(username=username, email=email, password_hash=hashed_password)

        # Save user to database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login page after registration

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")
        
    try:
        # Debug prints
        print("Request Method:", request.method)
        print("Content-Type:", request.headers.get('Content-Type'))
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        print(f"Received username: {username}")
        print(f"Received password: {password}")
    
        # Validate required fields
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        # Fetch user from database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Create JWT access token
            access_token = create_access_token(identity=user.id)
            
            # Return both the token and a success message
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "user_id": user.id,
                "username": user.username
            }), 200
        else:
            # Invalid credentials
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    # Get the user ID from the JWT token
    current_user_id = get_jwt_identity()
    
    # Get the user from the database
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "message": f"Profile Test successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200

#cards routes
@app.route('/cards', methods=['POST'])
@jwt_required()
def cards():
    return jsonify({"message": "All Cards Test successful"})

@app.route('/cards/<int:cards_id>', methods=['POST'])
@jwt_required()
def card_id(cards_id):
    return jsonify({"message": "Specific Cards Test successful"})

#collection routes
@app.route('/collection', methods=['POST'])
@jwt_required()
def collection():
    return jsonify({"message": "All Collections Test successful"})

if __name__ == "__main__":
    app.run(debug=True)
