import uuid
from flask import Blueprint, request, redirect, jsonify, session
from app.auth.oauth import get_auth_url, get_token_from_code, store_token, clear_token

# Create the Blueprint with the correct name
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Start OAuth login flow."""
    # Generate random state for CSRF protection
    state = str(uuid.uuid4())
    session['auth_state'] = state
    
    # Get authorization URL and redirect user
    auth_url = get_auth_url(state)
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    """Handle OAuth callback from Microsoft."""
    # Verify state for security
    if request.args.get('state') != session.get('auth_state'):
        return jsonify({"error": "State verification failed"}), 400
    
    # Check for error in response
    if 'error' in request.args:
        return jsonify({
            "error": request.args['error'],
            "error_description": request.args.get('error_description', '')
        }), 400
    
    # Exchange code for token
    if 'code' in request.args:
        token_data = get_token_from_code(request.args['code'])
        
        if 'error' in token_data:
            return jsonify({
                "error": token_data.get('error'),
                "error_description": token_data.get('error_description', '')
            }), 400
        
        # Store token and redirect to home
        store_token(token_data)
        return redirect('/')
    
    return jsonify({"error": "No authorization code received"}), 400

@auth_bp.route('/logout')
def logout():
    """Log user out by clearing token."""
    clear_token()
    return redirect('/')

@auth_bp.route('/status')
def status():
    """Check authentication status."""
    authenticated = 'token_data' in session
    return jsonify({"authenticated": authenticated})