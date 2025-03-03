"""
Microsoft Graph API Test Script
-------------------------------
This script tests your Graph API connection independent of the Flask application.
It implements the exact OAuth flow as described in the Microsoft documentation.

Usage:
1. Fill in your OAuth credentials below
2. Run this script
3. Follow the authentication instructions
4. The script will test your access to the Graph API
"""

import requests
import webbrowser
import urllib.parse
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Fill in your OAuth credentials
CLIENT_ID = ""  # Your application client ID
CLIENT_SECRET = ""  # Your client secret
REDIRECT_URI = "http://localhost:8000/callback"  # Must match your registered redirect URI
SCOPES = ["https://graph.microsoft.com/Mail.ReadWrite", 
          "https://graph.microsoft.com/Mail.Send",
          "https://graph.microsoft.com/User.Read",
          "offline_access"]
TENANT = "common"  # Use 'common' for both personal and work accounts

# Global variables
auth_code = None
access_token = None
callback_received = False

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, callback_received
        
        if self.path.startswith('/callback'):
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'code' in query_components:
                auth_code = query_components['code'][0]
                callback_received = True
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication successful!</h1><p>You can close this window now.</p></body></html>")
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication failed!</h1><p>No authorization code received.</p></body></html>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress logging
        return

def start_server():
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

def get_auth_url():
    """Generate authorization URL."""
    base_url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/authorize"
    
    # Format scopes exactly as shown in the documentation
    scope_string = " ".join(SCOPES)
    
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": scope_string,
        "state": "12345"  # A random state value
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return auth_url

def get_token_from_code(code):
    """Exchange authorization code for access token."""
    token_url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
    
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(SCOPES),
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    
    if response.ok:
        return response.json()
    else:
        print(f"Token request failed: {response.status_code}")
        print(response.text)
        return None

def test_graph_api(token):
    """Test Microsoft Graph API with the acquired token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test /me endpoint
    print("\n1. Testing /me endpoint...")
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        user_data = response.json()
        print(f"User: {user_data.get('displayName', 'Unknown')} ({user_data.get('userPrincipalName', 'Unknown')})")
    else:
        print(f"Error: {response.text}")
    
    # Test /me/messages endpoint
    print("\n2. Testing /me/messages endpoint...")
    response = requests.get('https://graph.microsoft.com/v1.0/me/messages?$top=1', headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        messages = response.json()
        if 'value' in messages and len(messages['value']) > 0:
            print("Successfully retrieved message(s)!")
            print(f"First message subject: {messages['value'][0].get('subject', 'No subject')}")
        else:
            print("No messages found or empty response")
    else:
        print(f"Error: {response.text}")
    
    # Test /me/mailFolders endpoint
    print("\n3. Testing /me/mailFolders endpoint...")
    response = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders', headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        folders = response.json()
        if 'value' in folders and len(folders['value']) > 0:
            print("Successfully retrieved mail folders!")
            print(f"Folders found: {len(folders['value'])}")
            for folder in folders['value'][:3]:  # Show first 3 folders
                print(f" - {folder.get('displayName', 'Unknown')}")
        else:
            print("No folders found or empty response")
    else:
        print(f"Error: {response.text}")

def main():
    global auth_code, access_token, callback_received
    
    print("Starting Microsoft Graph API test...")
    
    # Start the callback server
    server = start_server()
    print(f"Callback server started at {REDIRECT_URI}")
    
    # Get the authorization URL and open it in the browser
    auth_url = get_auth_url()
    print(f"Opening browser to: {auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for the callback
    print("Waiting for authentication callback...")
    start_time = time.time()
    while not callback_received:
        time.sleep(1)
        if time.time() - start_time > 300:  # 5 minute timeout
            print("Timeout waiting for authentication callback")
            server.shutdown()
            return
    
    # Exchange the authorization code for an access token
    print(f"Authorization code received! Exchanging for access token...")
    token_data = get_token_from_code(auth_code)
    
    if token_data and 'access_token' in token_data:
        access_token = token_data['access_token']
        print("Access token acquired successfully!")
        print(f"Token expires in: {token_data.get('expires_in', 'Unknown')} seconds")
        print(f"Scopes: {token_data.get('scope', 'Unknown')}")
        
        # Test the Graph API
        test_graph_api(access_token)
    else:
        print("Failed to acquire access token")
    
    # Shutdown the server
    server.shutdown()
    print("\nTest completed!")

if __name__ == "__main__":
    main()