
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Card
from app.db import db

cards_bp = Blueprint('cards', __name__, url_prefix='')

@cards_bp.route('/cards', methods=['GET'])
@jwt_required()
def get_cards():
    """
    Get all cards
    ---
    tags:
      - Cards
    security:
      - Bearer: []
    responses:
      200:
        description: List of cards
    """
    try:
        cards = Card.query.all()
        
        return jsonify({
            "cards": [{
                "id": card.id,
                "name": card.name,
                "set_name": card.set_name,
                "card_type": card.card_type,
                "rarity": card.rarity,
                "energy_type": card.energy_type,
                "hp": card.hp,
                "description": card.description
            } for card in cards]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/<string:id>/delete', methods=['POST'])
@jwt_required()
def delete_card(id):
    """
    Delete a specific card
    ---
    tags:
      - Cards
    security:
      - Bearer: []
    responses:
      200:
        description: Removed card from user's db
      404:
        description: Card not found
      500:
        description: An error occurred during deletion
    """
    try:
        card = Card.query.get(id)
        if not card:
            return jsonify({"message": f"Card with id '{id}' not found."}), 404

        # Delete the card, database will cascade the deletion
        db.session.delete(card)
        db.session.commit()
        return jsonify({"message": f"Card with id '{id}' and related entries in collections/decks have been deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while deleting the card.", "error": str(e)}), 500