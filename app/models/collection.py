
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, validates
from app.db import db

class Collection(db.Model):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    card_id = Column(String, ForeignKey('cards.id', ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    date_added = Column(DateTime, default=func.current_timestamp())
    card_condition = Column(String, default="Near Mint")

    # Relationships
    user = relationship("User", back_populates="collections")
    card = relationship("Card", back_populates="collections")

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 1:
            raise ValueError('Quantity must be at least 1')
        return quantity

    @validates('card_condition')
    def validate_card_condition(self, key, condition):
        valid_conditions = ['Near Mint', 'Lightly Played', 'Moderately Played', 'Heavily Played', 'Damaged']
        if condition not in valid_conditions:
            raise ValueError(f'Invalid card condition. Must be one of: {", ".join(valid_conditions)}')
        return condition