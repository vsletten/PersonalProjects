# app/__init__.py
import os
import logging
from flask import Flask, session
from flask_session import Session
from config import Config

def create_app():
    """
    Create and configure the Flask application.
    
    This function follows the application factory pattern to create a new Flask
    application instance with the appropriate configuration and registered blueprints.
    
    Returns:
        Flask: The configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure session
    Session(app)
    
    # Create directories for flask-session if they don't exist
    if app.config['SESSION_TYPE'] == 'filesystem':
        os.makedirs(app.config.get('SESSION_FILE_DIR', 'flask_session'), exist_ok=True)
    
    # Configure logging
    logging_level = getattr(logging, app.config['LOG_LEVEL'])
    logging.basicConfig(
        level=logging_level,
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.message_routes import message_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(message_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Home page route showing authentication status and basic navigation."""
        authenticated = 'token_data' in session
        return f"""
        <h1>Microsoft Graph API MCP Server</h1>
        <p>Authentication status: {'Authenticated' if authenticated else 'Not authenticated'}</p>
        <p>
            {'<a href="/auth/logout">Logout</a>' if authenticated else '<a href="/auth/login">Login</a>'}
        </p>
        <p>
            {'<a href="/api/messages">View Messages</a>' if authenticated else ''}
        </p>
        <p>
            {'<a href="/auth/token-info">View Token Info</a>' if authenticated else ''}
        </p>
        <p>
            {'<a href="/auth/debug-me">Debug User Info</a>' if authenticated else ''}
        </p>
        """
    
    return app
