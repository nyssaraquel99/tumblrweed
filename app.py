# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 04:45:49 2026

@author: nyssa

use flask to open local server and retrieve oauth tokens from tumblr
"""

from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
import os, secrets

# get secrets from .env file
load_dotenv()
CLIENT_ID = os.getenv("TUMBLR_CLIENT_ID")
CLIENT_SECRET = os.getenv("TUMBLR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TUMBLR_REDIRECT_URI","http://localhost:3000/callback")

# oauth sites provided by tumblr
REQUEST_TOKEN_URL = "https://www.tumblr.com/oauth/request_token"
AUTH_ENDPOINT = "https://www.tumblr.com/oauth/authorize"
TOKEN_ENDPOINT = "https://www.tumblr.com/oauth/access_token"


# create secret key to validate local server for tumblr
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_urlsafe(16))

# request information from tumblr
@app.route("/start")
def start():
    oauth = OAuth1Session(CLIENT_ID, client_secret=CLIENT_SECRET, callback_uri=REDIRECT_URI)
    try:
        fetch_resp = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    except Exception as e:
        app.logger.error("Request token fetch failed: %s", e)
        return "Failed to obtain request token; check logs", 500
    
    session["resource_owner_key"] = fetch_resp.get("oauth_token")
    session["resource_owner_secret"] = fetch_resp.get("oauth_token_secret")
    
    url = oauth.authorization_url(AUTH_ENDPOINT)
    return redirect(url)

# receive information from tumblr
@app.route("/callback")
def callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")
    if not oauth_token or not oauth_verifier:
        return "Missing oauth_token or oauth_verifier", 400
    
    resource_owner_key = session.get("resource_owner_key")
    resource_owner_secret = session.get("resource_owner_secret")
    if resource_owner_key != oauth_token:
        return "Mismatched oauth_token", 400
    
    oauth = OAuth1Session(
        CLIENT_ID,
        client_secret=CLIENT_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_verifier
        )
    
    try:
        tokens = oauth.fetch_access_token(TOKEN_ENDPOINT)
    except Exception as e:
        app.logger.error("Access token fetch failed %s", e)
        return "Failed to fetch access token; check logs", 500
    
    app.logger.info("Access tokens: %s", tokens)
    return "Authorized -- access tokens printed to console"

if __name__ == "__main__":
    # start web server
    app.run(host="localhost", port=3000, debug=True, use_reloader=False)