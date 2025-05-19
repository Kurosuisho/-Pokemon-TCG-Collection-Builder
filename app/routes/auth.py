import os
from urllib.parse import urlencode

from flask import Blueprint, redirect, url_for, session, current_app, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import oauth
from app.db import db
from app.models.user import User

auth_bp = Blueprint('auth0', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    redirect_uri = url_for('auth0.callback', _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = token.get('userinfo') or oauth.auth0.parse_id_token(token)
    email = userinfo['email']
    username = userinfo.get('nickname') or email.split('@')[0]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(os.urandom(16).hex()),
        )
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    })


@auth_bp.route('/logout')
def logout():
    session.clear()
    params = {
        'returnTo': url_for('index', _external=True),
        'client_id': current_app.config['AUTH0_CLIENT_ID'],
    }
    logout_url = (
        f"https://{current_app.config['AUTH0_DOMAIN']}"
        f"/v2/logout?{urlencode(params)}"
    )
    return redirect(logout_url)
