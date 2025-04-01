
import re
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship, validates
from app.db import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    date_joined = Column(DateTime, default=func.current_timestamp())
    last_login = Column(DateTime)
    
    # Relationships defined later
    collections = None
    decks = None

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