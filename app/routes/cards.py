
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Card

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