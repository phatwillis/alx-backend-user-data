#!/usr/bin/env python3
"""
Defines a hash_password function to return a hashed password
"""
import bcrypt
from bcrypt import hashpw


def hash_password(password: str) -> bytes:
    """
    Returns a hashed password
    Args:
        password (str): password to be hashed
    """
    # strings must be encoded before hashing
    password = password.encode()
    # hash the password
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    confirms a password is valid
    Args:
        hashed_password (bytes): hashed password
        password (str): password in string
    Return:
        bool
    """
    # strings must be encoded before hashing
    password = password.encode()
    validation = bcrypt.checkpw(password, hashed_password)
    return validation
    
