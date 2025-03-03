import os
import logging
from flask import Flask, session
from flask_session import Session
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure session
    Session(app)
    
    # Configure logging
    logging_level = getattr(logging, app.config['LOG_LEVEL'])
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create directories for flask-session if they don't exist
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.message_routes import message_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(message_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
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
        """
    
    return app