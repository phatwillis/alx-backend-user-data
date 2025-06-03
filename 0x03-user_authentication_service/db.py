#!/usr/bin/env python3
"""DB module
"""
from typing import Any, Dict, TypeVar
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from user import Base
from user import User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str,
                 hashed_password: str) -> TypeVar('User'):
        """adds new user and returns a User object"""
        new_user = User(email, hashed_password)
        self._session.add(new_user)
        self._session.commit()
        return new_user

    def find_user_by(self,
                     **kwargs: Dict[str, Any]) -> TypeVar('User'):
        """find user by keyword args specified"""
        found_user = self._session.query(User).filter_by(
            **kwargs).first()
        # passed kwargs using the ** syntax to unpack
        # the dictionary into keyword arguments.
        if found_user is None:
            raise NoResultFound
        return found_user

    def update_user(self, user_id: int,
                    **kwargs: Dict[str, Any]) -> None:
        """updates desired user specified by user id"""
        for k, v in kwargs.items():
            try:
                found_user = self.find_user_by(id=user_id)
            except NoResultFound:
                raise NoResultFound
            # set attribute of the found user
            if hasattr(found_user, k):
                setattr(found_user, k, v)
            else:
                raise ValueError
        self._session.commit()
