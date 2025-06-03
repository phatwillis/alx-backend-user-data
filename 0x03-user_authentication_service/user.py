#!/usr/bin/env python3
"""User Module"""
from typing import Any
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """Mapped User class"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(length=250))
    hashed_password = Column(String(length=250), nullable=False)
    session_id = Column(String(length=250), nullable=True)
    reset_token = Column(String(length=250), nullable=True)

    def __init__(self, email: str,
                 hashed_password: str,
                 session_id: str = None,
                 reset_token: str = None):
        """The initialiser"""
        super().__init__()
        self.email = email
        self.hashed_password = hashed_password
        self.session_id = session_id
        self.reset_token = reset_token
