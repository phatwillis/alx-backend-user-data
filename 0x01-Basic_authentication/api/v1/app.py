#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None
AUTH_TYPE = os.getenv("AUTH_TYPE")

if AUTH_TYPE == "basic_auth":
    from api.v1.auth.basic_auth import BasicAuth
    auth = BasicAuth()
if AUTH_TYPE == "auth":
    from api.v1.auth.auth import Auth
    auth = Auth()


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized_access(error) -> str:
    """error handler for status code 401"""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def access_forbidden(error) -> str:
    """error handler for status code 403"""
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def checking_auth() -> None:
    """check authentication"""
    if auth is None:
        return
    allowed_paths = ['/api/v1/status/',
                     '/api/v1/unauthorized/',
                     '/api/v1/forbidden/']
    requires_auth = auth.require_auth(request.path, allowed_paths)
    if requires_auth is False:  # if it does not require authentication
        pass
    else:
        # check that an auth header is present
        authorization_header = auth.authorization_header(request)
        if authorization_header is None:
            abort(401)

        # if auth header is present, check that the
        # current user is allowed
        authorized_user_check = auth.current_user(request)
        if authorized_user_check is None:
            abort(403)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
