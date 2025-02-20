import os
from dotenv import load_dotenv
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, create_engine, func
from sqlalchemy.orm import relationship, sessionmaker, validates
from pokemontcgsdk import Card as PokemonCard
from pokemontcgsdk import RestClient
import re

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

    def __repr__(self):
        return f'<User {self.username}>'
    
    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError('Invalid email address')
        return email

    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r"^[A-Za-z0-9_-]*$", username):
            raise ValueError('Username can only contain letters, numbers, underscores, and dashes')
        return username


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


class Collection(db.Model):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id', ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    date_added = Column(DateTime, default=func.current_timestamp())
    card_condition = Column(String, default="Near Mint")

    # Relationship defined AFTER all classes
    user = relationship("User", back_populates="collections")
    card = relationship("Card", backref="collections")

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 1:
            raise ValueError('Quantity must be at least 1')
        return quantity


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


class DeckCard(db.Model):
    __tablename__ = 'deck_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=func.current_timestamp())

    deck = relationship("Deck", backref="deck_cards")
    card = relationship("Card", backref="deck_cards")


# Fixing relationships **AFTER** all classes are declared
User.collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
User.decks = relationship("Deck", back_populates="user")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:Thisisatest25!@localhost:5432/Project Database')
engine = create_engine(DATABASE_URL)
db.Model.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()
