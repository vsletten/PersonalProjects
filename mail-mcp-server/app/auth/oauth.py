import requests
import time
import urllib.parse
import logging
from functools import wraps
from flask import session, redirect, jsonify
from config import Config

logger = logging.getLogger(__name__)

def get_auth_url(state):
    """Generate authorization URL for Microsoft OAuth."""
    base_url = f"https://login.microsoftonline.com/{Config.MS_TENANT_ID}/oauth2/v2.0/authorize"
    
    params = {
        "client_id": Config.MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.MS_REDIRECT_URI,
        "response_mode": "query",
        "scope": "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send offline_access",
        "state": state
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    logger.debug(f"Generated auth URL: {auth_url}")
    return auth_url

def get_token_from_code(code):
    """Exchange authorization code for access token."""
    token_url = f"https://login.microsoftonline.com/{Config.MS_TENANT_ID}/oauth2/v2.0/token"
    
    data = {
        "client_id": Config.MS_CLIENT_ID,
        "scope": "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send offline_access",
        "code": code,
        "redirect_uri": Config.MS_REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": Config.MS_CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    
    if response.ok:
        token_data = response.json()
        # Add expiration timestamp for easier refresh checking
        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)
        return token_data
    else:
        try:
            error_data = response.json()
        except:
            error_data = {"error": "Unknown error", "error_description": response.text}
        return error_data

def refresh_token(refresh_token):
    """Get new access token using refresh token."""
    token_url = f"https://login.microsoftonline.com/{Config.MS_TENANT_ID}/oauth2/v2.0/token"
    
    data = {
        "client_id": Config.MS_CLIENT_ID,
        "scope": "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send offline_access",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_secret": Config.MS_CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    
    if response.ok:
        token_data = response.json()
        # Add expiration timestamp
        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)
        return token_data
    else:
        try:
            error_data = response.json()
        except:
            error_data = {"error": "Unknown error", "error_description": response.text}
        return error_data

def get_token():
    """Get current access token, refreshing if needed."""
    token_data = session.get('token_data')
    
    if not token_data:
        return None
    
    # If token expires in less than 5 minutes, refresh it
    if token_data.get('expires_at', 0) < time.time() + 300:
        new_token_data = refresh_token(token_data.get('refresh_token'))
        
        if 'error' not in new_token_data:
            session['token_data'] = new_token_data
            return new_token_data.get('access_token')
        else:
            # If refresh failed, clear token data
            session.pop('token_data', None)
            return None
    
    return token_data.get('access_token')

def store_token(token_data):
    """Store token data in session."""
    session['token_data'] = token_data

def clear_token():
    """Remove token data from session."""
    if 'token_data' in session:
        session.pop('token_data')

def requires_auth(f):
    """Decorator for routes requiring authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        return f(*args, **kwargs)
    
    return decorated