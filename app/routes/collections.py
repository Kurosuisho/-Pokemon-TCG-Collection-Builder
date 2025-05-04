
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
      404:
        description: Card not found
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

        card = Card.query.get(card_id)
        if not card:
            return jsonify({"message": f"Card with id '{card_id}' not found."}), 404

        new_collection = Collection(
            user_id=current_user_id,
            card_id=card_id,
            quantity=quantity
        )
        db.session.add(new_collection)
        db.session.commit()

        return jsonify({
            "message": "Collection created successfully",
            "collection_id": new_collection.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@collections_bp.route('/collection/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_collection(id):
    """
    Delete a specific collection entry
    ---
    tags:
      - Collections
    parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: ID of the collection entry to delete
    security:
      - Bearer: []
    responses:
      200:
        description: Removed collection entry from user's db
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Collection entry not found
      500:
        description: An error occurred during deletion
    """
    try:
        current_user_id = get_jwt_identity()
        # fetch only if it belongs to this user
        coll = Collection.query.filter_by(id=id, user_id=current_user_id).first()
        if not coll:
            return jsonify({"message": f"Collection entry with id '{id}' not found."}), 404

        db.session.delete(coll)
        db.session.commit()
        return jsonify({
            "message": f"Collection entry with id '{id}' has been deleted."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "An error occurred while deleting the collection entry.",
            "error": str(e)
        }), 500