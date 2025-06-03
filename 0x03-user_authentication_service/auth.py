#!/usr/bin/env python3
"""authentication methods"""
from typing import TypeVar
from uuid import uuid4
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
from db import DB
from user import User


def _hash_password(password: str) -> bytes:
    """hashes a password using bcrypt"""
    password = password.encode()
    return bcrypt.hashpw(password, bcrypt.gensalt())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str,
                      password: str) -> TypeVar('User'):
        """method to register user"""
        try:
            user_check = self._db.find_user_by(email=email)
            if user_check is not None:
                raise ValueError("User {} already exists".format(email))
        except NoResultFound:
            hashedpassword = _hash_password(password)
            # since we have gotten a DB instance using self._db,
            # use add_user method from the DB class to create a new user.
            new_user = self._db.add_user(email, hashedpassword)

    def valid_login(self, email: str, password: str) -> bool:
        """checks if login is correct using bcrypt"""
        try:
            password = password.encode()
            this_user = self._db.find_user_by(email=email)
            password_check: bool = bcrypt.checkpw(password,
                                                  this_user.hashed_password)
            return password_check

        except NoResultFound:
            return False

    def _generate_uuid(self) -> str:
        """returns a string representation of a new UUID"""
        generated_uuid = uuid4()
        generated_uuid = str(generated_uuid)
        return generated_uuid

    def create_session(self, email: str) -> str:
        """creates a session id and returns it"""
        generated_id = self._generate_uuid()
        try:
            found_user = self._db.find_user_by(email=email)
            # update the user,
            # remember the update_user method does a session commit
            self._db.update_user(found_user.id,
                                 session_id=generated_id)
            return generated_id

        except NoResultFound:
            pass

    def get_user_from_session_id(self,
                                 session_id: str) -> TypeVar("User"):
        """gets a user using session_id"""
        if session_id is None:
            return None
        try:
            found_user = self._db.find_user_by(session_id=session_id)
            return found_user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: str) -> None:
        """destroys a session by
        updating the corresponding user's session ID to None"""
        try:
            self._db.update_user(user_id, session_id=None)
        except ValueError:
            return None
        return None

    def get_reset_password_token(self, email) -> None:
        """creates reset token
        and updates the user's reset_token"""
        try:
            user = self._db.find_user_by(email=email)
            reset_token = self._generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str,
                        password: str) -> None:
        """updates user password"""
        try:
            registered_user = self._db.find_user_by(reset_token=reset_token)
            hashed_pw = _hash_password(password)
            self._db.update_user(registered_user.id, hashed_password=hashed_pw)
        except NoResultFound:
            raise ValueError
