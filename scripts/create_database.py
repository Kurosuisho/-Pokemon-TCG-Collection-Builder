
import sys
import os
from app import create_app
from app.db import db
from app.models import Card
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = create_app()

def load_sample_cards(session):
    # Check if cards already exist
    if session.query(Card).count() > 0:
        print("Cards already exist in database")
        return
    
    # Sample data for 5 Pokemon cards
    sample_cards = [
        {"id": "card-1", "name": "Pikachu", "set_name": "Base Set", "card_type": "Pokémon", "rarity": "Common", "energy_type": "Electric", "hp": 40, "description": "When several of these Pokémon gather, their electricity could build and cause lightning storms.", "evolution_stage": "Basic", "weakness": "Fighting", "resistance": "None", "retreat_cost": 1},
        {"id": "card-2", "name": "Charizard", "set_name": "Base Set", "card_type": "Pokémon", "rarity": "Rare Holo", "energy_type": "Fire", "hp": 120, "description": "Spits fire that is hot enough to melt boulders. Known to cause forest fires unintentionally.", "evolution_stage": "Stage 2", "weakness": "Water", "resistance": "Fighting", "retreat_cost": 3},
        {"id": "card-3", "name": "Blastoise", "set_name": "Base Set", "card_type": "Pokémon", "rarity": "Rare Holo", "energy_type": "Water", "hp": 100, "description": "A brutal Pokémon with pressurized water jets on its shell. They are used for high-speed tackles.", "evolution_stage": "Stage 2", "weakness": "Lightning", "resistance": "None", "retreat_cost": 3},
        {"id": "card-4", "name": "Venusaur", "set_name": "Base Set", "card_type": "Pokémon", "rarity": "Rare Holo", "energy_type": "Grass", "hp": 100, "description": "The plant blooms when it is absorbing solar energy. It stays on the move to seek sunlight.", "evolution_stage": "Stage 2", "weakness": "Fire", "resistance": "None", "retreat_cost": 2},
        {"id": "card-5", "name": "Mewtwo", "set_name": "Base Set", "card_type": "Pokémon", "rarity": "Rare Holo", "energy_type": "Psychic", "hp": 60, "description": "A scientist created this Pokémin after years of horrific gene-splicing and DNA engineering experiments.", "evolution_stage": "Basic", "weakness": "Psychic", "resistance": "None", "retreat_cost": 3}
    ]
    
    print("Adding sample cards to database...")
    for card_data in sample_cards:
        if "created_at" in card_data:
            del card_data["created_at"]
        
        # Make sure resistance is None when "None" string is used
        if card_data.get("resistance") == "None":
            card_data["resistance"] = None

        attack_names = []
        if card_data["name"] == "Pikachu":
            attack_names = ["Thunder Shock", "Agility"]
        elif card_data["name"] == "Charizard":
            attack_names = ["Fire Spin", "Energy Burn"]
        elif card_data["name"] == "Blastoise":
            attack_names = ["Water Gun", "Hydro Pump"]
        elif card_data["name"] == "Venusaur":
            attack_names = ["Vine Whip", "Solar Beam"]
        elif card_data["name"] == "Mewtwo":
            attack_names = ["Psychic", "Barrier"]
        
        # Create the card without any None values for required fields
        card = Card(
            id=card_data["id"],
            name=card_data["name"],
            set_name=card_data["set_name"],
            card_type=card_data["card_type"],
            rarity=card_data["rarity"],
            energy_type=card_data["energy_type"],
            hp=card_data["hp"],
            attack_names=attack_names,
            description=card_data["description"],
            evolution_stage=card_data["evolution_stage"],
            weakness=card_data["weakness"],
            resistance=card_data["resistance"],
            retreat_cost=card_data["retreat_cost"]
        )
        session.add(card)
    
    try:
        session.commit()
        print("Sample cards added successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error adding sample cards: {e}")

if __name__ == "__main__":
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        session = db.session
        load_sample_cards(session)
        print("Database initialized successfully")