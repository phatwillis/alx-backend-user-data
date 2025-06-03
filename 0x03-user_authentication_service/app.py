#!/usr/bin/env python3
"""Basic Flask App"""
from flask import Flask, jsonify, make_response, redirect, request, abort
from auth import Auth
app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"], strict_slashes=False)
def simple_route():
    """returns welcome message"""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"],
           strict_slashes=False)
def users():
    """registers a user"""
    # retrieve email and password
    try:
        data = request.form
        email = data.get("email")
        password = data.get("password")
    except Exception:
        pass

    try:
        AUTH.register_user(email, password)
        return jsonify({"email": "{}".format(email),
                        "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"})


@app.route("/sessions", methods=["POST"],
           strict_slashes=False)
def login() -> str:
    """login function"""
    try:
        data = request.form
        email = data.get("email")
        password = data.get("password")
    except Exception:
        pass

    # check if the login details are valid
    valid_login = AUTH.valid_login(email, password)
    if valid_login is True:
        # create a session for that user
        user_session_id = AUTH.create_session(email)
        response = jsonify(
            {"email": "{}".format(email), "message": "logged in"})
        response.set_cookie("session_id", user_session_id)
        return response
    else:
        abort(401)


@app.route("/sessions", methods=["DELETE"],
           strict_slashes=False)
def logout():
    """logout function"""
    session_id = request.cookies.get("session_id", None)
    user_with_session = AUTH.get_user_from_session_id(session_id)
    if user_with_session is None or session_id is None:
        abort(403)

    # destroy the session by
    # updating the corresponding user's session ID to None
    AUTH.destroy_session(user_with_session.id)
    return redirect("/")


@app.route("/profile", methods=["GET"],
           strict_slashes=False)
def profile() -> str:
    """profile function to respond to the GET /profile route."""
    session_id = request.cookies.get("session_id")
    user_with_session = AUTH.get_user_from_session_id(session_id)
    if user_with_session is None:
        abort(403)
    resp = jsonify({"email": user_with_session.email}), 200
    return resp


@app.route("/reset_password", methods=["POST"],
           strict_slashes=False)
def get_reset_password_token():
    """get reset password token"""
    try:
        data = request.form
        email = data.get("email")
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email,
                        "reset_token": reset_token}), 200

    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"],
           strict_slashes=False)
def update_password() -> str:
    """update password endpoint"""
    try:
        # get data from request form
        data = request.form
        email = data.get("email")
        new_password = data.get("password")
        reset_token = data.get("reset_token")

        # update the password
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email,
                        "message": "Password updated"}), 200

    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
