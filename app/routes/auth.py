
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db
from app.models import User, Collection, Deck
from app.utils import sanitize_input, is_valid_email, is_valid_username

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User registered
      404:
        description: Unable to register user
    """
    try:
        username = sanitize_input(request.json.get("username"))
        email = sanitize_input(request.json.get("email"))
        password = request.json.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Missing username, email, or password"}), 400

        if not is_valid_username(username):
            return jsonify({"error": "Invalid username format"}), 400

        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        # Auto-login after registration
        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "message": "Registration successful",
            "access_token": access_token,
            "user_id": new_user.id,
            "username": new_user.username
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: Can be username or email
            password:
              type: string
    responses:
      200:
        description: Login successful
      400:
        description: Missing credentials or invalid format
      401:
        description: Invalid username or password
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        if "@" in username and not is_valid_email(username):
            return jsonify({"error": "Invalid email format"}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=str(user.id))

            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "user_id": user.id,
                "username": user.username
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Profile retrieved successfully
      404:
        description: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    user_collections = Collection.query.filter_by(user_id=current_user_id).all()
    user_decks = Deck.query.filter_by(user_id=current_user_id).all()

    return jsonify({
        "message": "Profile retrieved successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "collections": [{"id": c.id, "card_id": c.card_id, "quantity": c.quantity} for c in user_collections],
            "decks": [{"id": d.id, "name": d.name, "description": d.description} for d in user_decks]
        }
    }), 200