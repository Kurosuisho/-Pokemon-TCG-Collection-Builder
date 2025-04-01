
from flask import Blueprint, request, jsonify, session
from app.services.ai_service import PokemonAIService

# Initialize the blueprint
chat_bp = Blueprint('chat', __name__)

# Shared AI service instance
ai_service = PokemonAIService()

@chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Ask the AI a question
    ---
    tags:
      - Chat
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
            chat_reset:
              type: boolean
    responses:
      200:
        description: AI response
      400:
        description: Missing question
      500:
        description: AI service error
    """
    
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required'}), 400
    
    question = data['question']
    
    # Resets chat 
    if 'chat_reset' in data and data['chat_reset']:
        ai_service.reset_chat()
    
    # Get response from AI
    result = ai_service.ask_question(question)
    
    if result['status'] == 'success':
        return jsonify({'response': result['response']})
    else:
        return jsonify({'error': result['message']}), 500

@chat_bp.route('/reset', methods=['POST'])
def reset_chat():
    ai_service.reset_chat()
    return jsonify({'message': 'Chat session reset successfully'})