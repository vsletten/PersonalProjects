import uuid
import json
import logging
from flask import Blueprint, request, redirect, jsonify, session
from app.auth.oauth import get_auth_url, get_token_from_code, store_token, clear_token, get_token

# Configure logger
logger = logging.getLogger(__name__)

# Create the Blueprint with the correct name
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Start OAuth login flow."""
    # Generate random state for CSRF protection
    state = str(uuid.uuid4())
    session['auth_state'] = state
    
    logger.info("Starting OAuth login flow")
    # Get authorization URL and redirect user
    auth_url = get_auth_url(state)
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    """Handle OAuth callback from Microsoft."""
    logger.info("Received OAuth callback")
    
    # Verify state for security
    if request.args.get('state') != session.get('auth_state'):
        logger.warning("State verification failed")
        return jsonify({"error": "State verification failed"}), 400
    
    # Check for error in response
    if 'error' in request.args:
        error = request.args.get('error')
        error_description = request.args.get('error_description', '')
        logger.error(f"OAuth error: {error} - {error_description}")
        return jsonify({
            "error": error,
            "error_description": error_description
        }), 400
    
    # Exchange code for token
    if 'code' in request.args:
        logger.info("Exchanging authorization code for token")
        token_data = get_token_from_code(request.args['code'])
        
        if 'error' in token_data:
            logger.error(f"Token error: {token_data.get('error')} - {token_data.get('error_description', '')}")
            return jsonify({
                "error": token_data.get('error'),
                "error_description": token_data.get('error_description', '')
            }), 400
        
        # Store token and redirect to home
        logger.info("Token obtained successfully")
        store_token(token_data)
        return redirect('/')
    
    logger.warning("No authorization code received")
    return jsonify({"error": "No authorization code received"}), 400

@auth_bp.route('/logout')
def logout():
    """Log user out by clearing token."""
    logger.info("Logging out user")
    clear_token()
    return redirect('/')

@auth_bp.route('/status')
def status():
    """Check authentication status."""
    authenticated = 'token_data' in session
    logger.info(f"Auth status check: authenticated={authenticated}")
    return jsonify({"authenticated": authenticated})

@auth_bp.route('/token-info')
def token_info():
    """Debug endpoint to view token information."""
    token_data = session.get('token_data', {})
    
    # Remove the actual tokens for security
    safe_data = {k: v for k, v in token_data.items() if k not in ['access_token', 'refresh_token']}
    
    # If we have a token, try to get the scopes
    if 'scope' in token_data:
        scopes = token_data['scope'].split()
        safe_data['scopes'] = scopes
    
    # Check if token is expired
    import time
    if 'expires_at' in token_data:
        safe_data['expires_in_seconds'] = int(token_data['expires_at'] - time.time())
        safe_data['is_expired'] = safe_data['expires_in_seconds'] <= 0
    
    return jsonify(safe_data)

@auth_bp.route('/debug-me')
def debug_me():
    """Debug endpoint to fetch user profile."""
    import requests
    
    token = get_token()
    if not token:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Try to get user profile
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # First try /me endpoint
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        user_data = response.json()
        
        # Then try to list available mailboxes
        mailbox_response = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders', headers=headers)
        mailbox_data = mailbox_response.json()
        
        return jsonify({
            "user": user_data,
            "mailboxes": mailbox_data
        })
    except Exception as e:
        logger.exception("Error in debug endpoint")
        return jsonify({"error": str(e)}), 500