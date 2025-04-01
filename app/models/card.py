
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, func
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