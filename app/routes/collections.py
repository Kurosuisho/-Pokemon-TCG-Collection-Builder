
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Collection, Card

collections_bp = Blueprint('collections', __name__, url_prefix='')

@collections_bp.route('/collection', methods=['GET'])
@jwt_required()
def get_user_collection():
    """
    Get current user's collection
    ---
    tags:
      - Collections
    security:
      - Bearer: []
    responses:
      200:
        description: User's card collection
    """
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

@collections_bp.route('/collection/create', methods=['POST'])
@jwt_required()
def create_collection():
    """
    Create a collection for the current user
    ---
    tags:
      - Collections
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            card_id:
              type: string
            quantity:
              type: integer
    responses:
      201:
        description: Collection created successfully
      400:
        description: Missing card ID or bad input
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing or invalid JSON body"}), 400

        card_id = data.get("card_id")
        quantity = data.get("quantity", 1)

        if not card_id:
            return jsonify({"error": "Card ID is required"}), 400

        new_collection = Collection(user_id=current_user_id, card_id=card_id, quantity=quantity)
        db.session.add(new_collection)
        db.session.commit()

        return jsonify({
            "message": "Collection created successfully",
            "collection_id": new_collection.id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
