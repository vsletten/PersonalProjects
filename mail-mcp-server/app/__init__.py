import logging
from flask import Flask
from flask_session import Session
from config import Config

# Initialize Flask-Session
session = Session()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    session.init_app(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.message_routes import message_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(message_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            "message": "MCP Server for Microsoft Graph API",
            "version": "1.0.0"
        }
    
    return app
