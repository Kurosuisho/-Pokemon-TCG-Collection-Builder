
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Deck, DeckCard, Collection
from app.utils import sanitize_input

decks_bp = Blueprint('decks', __name__, url_prefix='')

@decks_bp.route('/deck/create', methods=['POST'])
@jwt_required()
def create_deck():
    """
    Create a new deck
    ---
    tags:
      - Decks
    security:
      - Bearer: [""]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Deck created
      400:
        description: Invalid input
    """
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

@decks_bp.route('/deck/<int:deck_id>/add-card', methods=['POST'])
@jwt_required()
def add_card_to_deck(deck_id):
    """
    Add a card to a specific deck
    ---
    tags:
      - Decks
    consumes:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: path
        name: deck_id
        type: integer
        required: true
        description: ID of the deck to add the card to
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - card_id
          properties:
            card_id:
              type: string
              description: The `id` of the card to add
            quantity:
              type: integer
              description: Number of copies to add (default 1)
    responses:
      201:
        description: Card added to deck successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Invalid input or not enough cards in collection
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Deck not found or access denied
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json(force=True)
        card_id = data.get('card_id')
        quantity = data.get('quantity', 1)

        if not card_id:
            return jsonify({"error": "card_id is required"}), 400

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

        # Check total after adding
        existing = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
        new_total = quantity + (existing.quantity if existing else 0)
        if new_total > user_collection.quantity:
            return jsonify({"error": "Not enough cards in your collection"}), 400

        # Add or update
        if existing:
            existing.quantity = new_total
        else:
            db.session.add(DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity))

        db.session.commit()
        return jsonify({"message": "Card added to deck successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
      
@decks_bp.route('/deck', methods=['GET'])
@jwt_required()
def list_decks():
    """
    List all decks for the current user
    ---
    tags:
      - Decks
    security:
      - Bearer: []
    responses:
      200:
        description: A list of decks
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
              is_public:
                type: boolean
              created_at:
                type: string
                format: date-time
              last_updated:
                type: string
                format: date-time
    """
    try:
        current_user_id = get_jwt_identity()
        decks = Deck.query.filter_by(user_id=current_user_id).all()

        result = []
        for deck in decks:
            result.append({
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "is_public": deck.is_public,
                "created_at": deck.created_at.strftime('%Y-%m-%d'),
                "last_updated": deck.last_updated.strftime('%Y-%m-%d'),
                "card_count": sum(dc.quantity for dc in deck.deck_cards)
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
