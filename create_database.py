import os
from dotenv import load_dotenv
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, create_engine, func
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from pokemontcgsdk import Card as PokemonCard
from pokemontcgsdk import RestClient


load_dotenv("data/.env")


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_picture = db.Column(String)
    date_joined = db.Column(DateTime, default=func.current_timestamp())
    last_login = db.Column(DateTime)

    collections = relationship("Collection", back_populates="user")
    decks = relationship("Deck", back_populates="user")
    
    def __repr__(self):
        return f'<User {self.username}>'


class Card(db.Model):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    set_name = Column(String, nullable=False)
    card_type = Column(String)
    rarity = Column(String)
    energy_type = Column(String)
    hp = Column(Integer)
    attack_names = Column(JSON)
    description = Column(Text)
    evolution_stage = Column(String)
    weakness = Column(String)
    resistance = Column(String)
    retreat_cost = Column(Integer)
    created_at = Column(DateTime, default=func.current_timestamp())

    collections = relationship("Collection", back_populates="card")
    deck_cards = relationship("DeckCard", back_populates="card")


class Collection(db.Model):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date_added = Column(DateTime, default=func.current_timestamp())
    card_condition = Column(String, default="Near Mint")

    user = relationship("User", back_populates="collections")
    card = relationship("Card", back_populates="collections")


class Deck(db.Model):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    last_updated = Column(DateTime, default=func.current_timestamp())

    user = relationship("User", back_populates="decks")
    deck_cards = relationship("DeckCard", back_populates="deck")


class DeckCard(db.Model):
    __tablename__ = 'deck_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=func.current_timestamp())

    deck = relationship("Deck", back_populates="deck_cards")
    card = relationship("Card", back_populates="deck_cards")


# Database configuration
db_directory = "D:/Sonstiges/Code Arbeiten/Masterschool/Backend Project/data"
db_name = "database.db"
db_path = f"{db_directory}/{db_name}"

engine = create_engine(f"sqlite:///{db_path}")
db.Model.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()


def fetch_pokemon_cards():
    # Get the API key and set it up   
    api_key = os.getenv('POKEMON_API_KEY') 
    RestClient.configure(api_key)
    
    # Get all cards
    all_cards = PokemonCard.all()
    if all_cards is None:
        raise ValueError("No cards were fetched from the API. Check your API key or connectivity.")
    
    return all_cards


def insert_pokemon_cards(cards):
    if not cards:
        print("No cards to process.")
        return
    
    total_cards = len(cards)
    print(f"Found {total_cards} cards to process")
    
    for index, card in enumerate(cards, 1):
        try:
            # Show progress every 10 cards
            if index % 10 == 0:
                progress = (index / total_cards) * 100
                # print(f"Processing card {index}/{total_cards} ({progress:.1f}%)...")
            
            # Safely handle retreat cost
            retreat_cost = len(card.retreat_cost) if hasattr(card, 'retreat_cost') and card.retreat_cost else None
            
            # Safely handle HP
            hp = int(card.hp) if hasattr(card, 'hp') and card.hp and card.hp.isdigit() else None
            
            # Safely handle energy type
            energy_type = card.types[0] if hasattr(card, 'types') and card.types else None
            
            # Safely handle attacks
            attack_names = [attack.name for attack in card.attacks] if hasattr(card, 'attacks') and card.attacks else []
            
            # Safely handle description
            if hasattr(card, 'flavorText') and card.flavorText:
                description = card.flavorText
            elif hasattr(card, 'text') and card.text:
                description = card.text[0]
            else:
                description = ''
            
            # Safely handle weaknesses
            weakness = ', '.join([w.type for w in card.weaknesses]) if hasattr(card, 'weaknesses') and card.weaknesses else None
            
            # Safely handle resistances
            resistance = ', '.join([r.type for r in card.resistances]) if hasattr(card, 'resistances') and card.resistances else None

            # Create a new card
            new_card = Card(
                name=card.name,
                set_name=card.set.name if hasattr(card, 'set') and card.set else None,
                card_type=card.supertype if hasattr(card, 'supertype') else None,
                rarity=card.rarity if hasattr(card, 'rarity') else None,
                energy_type=energy_type,
                hp=hp,
                attack_names=attack_names,
                description=description,
                evolution_stage=card.evolvesFrom if hasattr(card, 'evolvesFrom') else None,
                weakness=weakness,
                resistance=resistance,
                retreat_cost=retreat_cost,
            )
            
            # Add the card to the database
            session.add(new_card)
            
            # Commit every 100 cards to avoid memory issues
            if index % 100 == 0:
                session.commit()
                print(f"Saved {index} cards to database...")
        
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error processing card at index {index}: {e}")
    
    # Final commit for remaining cards
    session.commit()
    print(f"Finished processing all {total_cards} cards!")


def main():
    try:
        print("Starting Pokemon card fetch...")
        print("This might take a few minutes...")
        cards = fetch_pokemon_cards()
        
        if cards:
            print("\nStarting database insertion...")
            insert_pokemon_cards(cards)
            print("\nAll done! Cards have been successfully added to the database!")
        else:
            print("No cards fetched. Exiting.")
            
    except Exception as e:
        print("\nAn error occurred:")
        print(f"Error: {e}")


if __name__ == '__main__':
    main()