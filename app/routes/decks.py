
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
      - Bearer: []
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
      security:
        - Bearer: []
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
          description: Card added to the deck
        400:
          description: Invalid input
      """
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