from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db import db

class Deck(db.Model):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    last_updated = Column(DateTime, default=func.current_timestamp())
    
    # relationships
    user = relationship("User", back_populates="decks")

    deck_cards = relationship(
        "DeckCard",
        back_populates="deck",
        cascade="all, delete-orphan"
    )
    
    cards = relationship(
        "Card",
        secondary="deck_cards",
        viewonly=True,
        back_populates="decks"
    )


class DeckCard(db.Model):
    __tablename__ = 'deck_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=func.current_timestamp())
    
    deck = relationship("Deck", back_populates="deck_cards")
    card = relationship("Card", back_populates="deck_cards")
