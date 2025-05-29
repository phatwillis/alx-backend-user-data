#!/usr/bin/env python3
"""authentication class created here"""

from typing import List
from flask import request


class Auth:
    """Authentication class"""

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Define which routes don't need authentication
        exluded paths do not require authentication
        if function returns true, path is not in excluded path
        so it requires authentication"""
        if path is not None:
            if path[-1] != "/":
                path = path + "/"  # include the last slash
        if path is None:
            return True
        if excluded_paths is None or excluded_paths == []:
            return True
        if path not in excluded_paths:
            return True
        elif path in excluded_paths:
            return False  # does not need authentication

    def authorization_header(self, request=None) -> str:
        """authorization header function"""
        if request is None:
            return None
        elif request.headers.get("Authorization") is None:
            return None
        else:
            return request.headers.get("Authorization")

    def current_user(self, request=None) -> str:
        """current user function"""
        return None
