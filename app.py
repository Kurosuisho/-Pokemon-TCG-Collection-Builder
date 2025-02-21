import bleach
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_talisman import Talisman
from dotenv import load_dotenv
import os
import re
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from create_database import Card, DeckCard, db, User, Collection, Deck
from pokemontcgsdk import Card as PokemonCard

# Load environment variables
load_dotenv()

app = Flask(__name__)
talisman = Talisman(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Thisisatest25!@localhost:5432/Project Database"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cors = CORS(app)

limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

# Utility Functions
def sanitize_input(input_str):
    return bleach.clean(input_str)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_username(username):
    return re.match(r"^[A-Za-z0-9_-]{3,}$", username)

# User Authentication Routes
@app.route('/auth/register', methods=['POST'])
def register():
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
            "username": new_user.username,
            "redirect": url_for('me')
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
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
                "username": user.username,
                "redirect": url_for('me')
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
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

# Collection Routes
@app.route('/collection/create', methods=['POST'])
@jwt_required()
def create_collection():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        card_id = data.get("card_id")
        quantity = data.get("quantity", 1)

        if not card_id:
            return jsonify({"error": "Card ID is required"}), 400

        new_collection = Collection(user_id=current_user_id, card_id=card_id, quantity=quantity)
        db.session.add(new_collection)
        db.session.commit()

        return jsonify({"message": "Collection created successfully", "collection_id": new_collection.id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Deck Routes
@app.route('/deck/create', methods=['POST'])
@jwt_required()
def create_deck():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        name = sanitize_input(data.get("name"))
        description = sanitize_input(data.get("description", ""))

        if not name:
            return jsonify({"error": "Deck name is required"}), 400

        new_deck = Deck(user_id=current_user_id, name=name, description=description)
        db.session.add(new_deck)
        db.session.commit()

        return jsonify({"message": "Deck created successfully", "deck_id": new_deck.id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cards', methods=['GET'])
@jwt_required()
def get_cards():
    try:
        # Check if database already has cards
        cards = Card.query.all()

        if not cards:
            # Fetch cards using the Pokemon TCG SDK
            fetched_cards = PokemonCard.all()  # This fetches all cards

            for card in fetched_cards:
                # Ensure card ID is unique before inserting
                existing_card = Card.query.get(card.id)
                if not existing_card:
                    new_card = Card(
                        id=card.id,  # Use official ID
                        name=card.name,
                        set_name=card.set.name if card.set else None,
                        card_type=", ".join(card.types) if hasattr(card, "types") else None,
                        rarity=card.rarity,
                        energy_type=", ".join(card.subtypes) if hasattr(card, "subtypes") else None,
                        hp=int(card.hp) if card.hp and card.hp.isdigit() else None
                    )
                    db.session.add(new_card)

            db.session.commit()  # Commit new cards
            cards = Card.query.all()  # Re-fetch all cards

        # Convert cards to JSON
        return jsonify({
            "cards": [{
                "id": card.id,
                "name": card.name,
                "set_name": card.set_name,
                "card_type": card.card_type,
                "rarity": card.rarity,
                "energy_type": card.energy_type,
                "hp": card.hp
            } for card in cards]
        }), 200

    except Exception as e:
        db.session.rollback()  # Rollback if error occurs
        return jsonify({"error": str(e)}), 500


@app.route('/collection', methods=['GET'])
@jwt_required()
def get_user_collection():
    try:
        current_user_id = get_jwt_identity()
        collections = Collection.query.filter_by(user_id=current_user_id).all()
        
        collection_data = []
        for collection in collections:
            card = Card.query.get(collection.card_id)
            if card:
                collection_data.append({
                    "collection_id": collection.id,
                    "card_id": card.id,
                    "card_name": card.name,
                    "quantity": collection.quantity,
                    "condition": collection.card_condition
                })
        
        return jsonify({"collections": collection_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deck/<int:deck_id>/add-card', methods=['POST'])
@jwt_required()
def add_card_to_deck(deck_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        card_id = data.get('card_id')
        quantity = data.get('quantity', 1)

        # Verify deck ownership
        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({"error": "Deck not found or access denied"}), 404

        # Check if user has this card in their collection
        user_collection = Collection.query.filter_by(
            user_id=current_user_id,
            card_id=card_id
        ).first()
        
        if not user_collection:
            return jsonify({"error": "Card not in your collection"}), 400

        # Check if user has enough cards in collection
        existing_deck_cards = DeckCard.query.filter_by(
            deck_id=deck_id,
            card_id=card_id
        ).first()

        total_quantity = quantity
        if existing_deck_cards:
            total_quantity += existing_deck_cards.quantity

        if total_quantity > user_collection.quantity:
            return jsonify({"error": "Not enough cards in your collection"}), 400

        # Add card to deck
        if existing_deck_cards:
            existing_deck_cards.quantity = total_quantity
        else:
            deck_card = DeckCard(
                deck_id=deck_id,
                card_id=card_id,
                quantity=quantity
            )
            db.session.add(deck_card)

        db.session.commit()
        return jsonify({"message": "Card added to deck successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
