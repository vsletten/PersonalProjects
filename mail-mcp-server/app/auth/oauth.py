import requests
import time
import urllib.parse
import logging
from functools import wraps
from flask import session, redirect, jsonify
from config import Config

logger = logging.getLogger(__name__)

def get_auth_url(state):
    """
    Generate authorization URL for Microsoft OAuth.
    
    This is the first step in the OAuth 2.0 authorization code flow.
    The user will be redirected to Microsoft's login page to authenticate
    and authorize access to the requested scopes.
    
    Args:
        state (str): A unique state value to protect against CSRF attacks
        
    Returns:
        str: The authorization URL that the user should be redirected to
    """
    # Use 'common' endpoint to support both personal and work accounts
    base_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    
    # Format scopes exactly as shown in the Microsoft documentation
    # Must use full URI format (https://graph.microsoft.com/{scope})
    # This is critical for proper authentication with Microsoft Graph API
    scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
    
    params = {
        "client_id": Config.MS_CLIENT_ID,
        "response_type": "code",  # For authorization code flow
        "redirect_uri": Config.MS_REDIRECT_URI,
        "response_mode": "query",  # Return params in query string
        "scope": scope_string,
        "state": state  # CSRF protection
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    logger.debug(f"Generated auth URL: {auth_url}")
    return auth_url

def get_token_from_code(code):
    """
    Exchange authorization code for access token.
    
    This is the second step in the OAuth 2.0 authorization code flow.
    After the user authorizes the app, the authorization server returns a code
    which is exchanged here for an access token.
    
    Args:
        code (str): The authorization code received from the auth server
        
    Returns:
        dict: Token data including access_token, refresh_token, and expiration
    """
    token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    # Use the exact same scope string for consistency with the authorization request
    scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
    
    data = {
        "client_id": Config.MS_CLIENT_ID,
        "scope": scope_string,
        "code": code,
        "redirect_uri": Config.MS_REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": Config.MS_CLIENT_SECRET
    }
    
    logger.debug(f"Requesting token with data: {data}")
    response = requests.post(token_url, data=data)
    
    if response.ok:
        token_data = response.json()
        # Add expiration timestamp for easier refresh checking
        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)
        logger.debug(f"Token received successfully")
        return token_data
    else:
        logger.error(f"Token request failed: {response.status_code} - {response.text}")
        try:
            error_data = response.json()
        except:
            error_data = {"error": "Unknown error", "error_description": response.text}
        return error_data

def refresh_token(refresh_token):
    """
    Get new access token using refresh token.
    
    This function is used when an access token has expired and we want to
    get a new one without requiring the user to log in again.
    
    Args:
        refresh_token (str): The refresh token to use for getting a new access token
        
    Returns:
        dict: New token data including new access_token and refresh_token
    """
    token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    # Use the exact same scope string for consistency
    scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
    
    data = {
        "client_id": Config.MS_CLIENT_ID,
        "scope": scope_string,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_secret": Config.MS_CLIENT_SECRET
    }
    
    logger.debug(f"Refreshing token")
    response = requests.post(token_url, data=data)
    
    if response.ok:
        token_data = response.json()
        # Add expiration timestamp
        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)
        logger.debug(f"Token refreshed successfully")
        return token_data
    else:
        logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
        try:
            error_data = response.json()
        except:
            error_data = {"error": "Unknown error", "error_description": response.text}
        return error_data

def get_token():
    """
    Get current access token, refreshing if needed.
    
    This function checks if we have a valid token in the session.
    If the token is about to expire, it automatically refreshes it.
    
    Returns:
        str: The current valid access token or None if not authenticated
    """
    token_data = session.get('token_data')
    
    if not token_data:
        logger.debug("No token found in session")
        return None
    
    # If token expires in less than 5 minutes, refresh it
    if token_data.get('expires_at', 0) < time.time() + 300:
        logger.debug("Token about to expire, refreshing")
        new_token_data = refresh_token(token_data.get('refresh_token'))
        
        if 'error' not in new_token_data:
            session['token_data'] = new_token_data
            return new_token_data.get('access_token')
        else:
            # If refresh failed, clear token data
            logger.error(f"Token refresh failed: {new_token_data.get('error')}")
            session.pop('token_data', None)
            return None
    
    logger.debug("Using existing token")
    return token_data.get('access_token')

def store_token(token_data):
    """
    Store token data in session.
    
    Args:
        token_data (dict): Token data including access_token and refresh_token
    """
    logger.debug("Storing token in session")
    session['token_data'] = token_data

def clear_token():
    """Remove token data from session."""
    if 'token_data' in session:
        logger.debug("Clearing token from session")
        session.pop('token_data')

def requires_auth(f):
    """
    Decorator for routes requiring authentication.
    
    This decorator checks if the user is authenticated before allowing
    access to protected routes. If not authenticated, it returns a 401 response.
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        
        if not token:
            logger.warning("Authentication required but no token available")
            return jsonify({"error": "Authentication required"}), 401
        
        return f(*args, **kwargs)
    
    return decorated