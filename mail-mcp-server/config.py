import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Microsoft Graph API Credentials
    MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
    MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "")
    MS_TENANT_ID = os.getenv("MS_TENANT_ID", "")
    MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI", "http://localhost:5000/auth/callback")
    
    # MS Graph API Base URL
    MS_GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    # OAuth Scopes for Microsoft Graph API - Updated with more comprehensive scopes
    MS_GRAPH_SCOPES = [
        "Mail.ReadWrite",
        "Mail.ReadWrite.Shared",
        "Mail.Send",
        "Mail.Send.Shared",
        "MailboxSettings.Read",
        "User.Read",
        "offline_access"
    ]
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_FILE_DIR = os.getenv("SESSION_FILE_DIR", "flask_session")
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Cache settings
    CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "300"))  # 5 minutes
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")