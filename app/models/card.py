
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, func
from sqlalchemy.orm import relationship
from app.db import db

class Card(db.Model):
    __tablename__ = 'cards'

    id = Column(String(50), primary_key=True)
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
    
    collections = relationship(
        "Collection",
        back_populates="card",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    deck_cards = relationship(
        "DeckCard",
        back_populates="card",
        cascade="all, delete-orphan"
    )
    
    decks = relationship(
        "Deck",
        secondary="deck_cards",
        viewonly=True,
        back_populates="cards"
    )