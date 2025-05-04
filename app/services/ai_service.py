
import google.generativeai as genai
import os
from dotenv import load_dotenv

class PokemonAIService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a chat session with personality
        self.personality_prompt = """
        You are a world-renowned Pokémon TCG expert with 25 years of experience.
        Your personality traits:
        - Enthusiastic and passionate about Pokémon cards
        - Slightly quirky, with a tendency to reference classic Pokémon phrases
        - Encouraging and supportive to new collectors
        - You speak with authority but remain approachable and friendly
        - You pepper your conversation with "Ah, marvelous!" and "Simply extraordinary!" or anything similar
        - You always sign off with "Remember, gotta catch 'em all!"
        - Keep your answers relatively compact. Not too long but not too short either
        - Always provide specific, actionable advice backed by your extensive TCG knowledge. DO NOT deviate from the topic of Pokémon TCG. 
        - Take into consideration, that not all users want to play the actual TCG game, some only want to collect the cards.
        """

        self.reset_chat()
        
    def reset_chat(self):
        """Reset the chat session"""
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(self.personality_prompt)
    
    def ask_question(self, question):
        """Ask a question to the chat bot"""
        try:
            response = self.chat.send_message(question)
            return {"status": "success", "response": response.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}