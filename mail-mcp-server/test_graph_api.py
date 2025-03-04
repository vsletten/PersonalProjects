"""
Microsoft Graph API Test Script
-------------------------------
This script tests your Graph API connection independent of the Flask application.
It implements the exact OAuth flow as described in the Microsoft documentation.

Usage:
1. Run this script (it uses Config from your project)
2. Follow the authentication instructions in your browser
3. The script will test your access to the Graph API
"""

import requests
import webbrowser
import urllib.parse
import json
import time
import threading
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import the Config class from your project
from config import Config

# Get credentials from Config
CLIENT_ID = Config.MS_CLIENT_ID
CLIENT_SECRET = Config.MS_CLIENT_SECRET
REDIRECT_URI = "http://localhost:5000/auth/callback"  # Different from app for testing
TENANT = "common"  # Use 'common' for personal accounts

# Global variables
auth_code = None
access_token = None
callback_received = False

class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the OAuth callback."""
    
    def do_GET(self):
        """Handle GET requests - captures the authorization code."""
        global auth_code, callback_received
        
        if self.path.startswith('/auth/callback'):
            # Parse query parameters from the callback URL
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            if 'code' in query_components:
                # Successfully received the authorization code
                auth_code = query_components['code'][0]
                callback_received = True
                
                # Return a success page to the user
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #4CAF50;">Authentication successful!</h1>
                            <p>You have successfully authenticated with Microsoft Graph API.</p>
                            <p>You can close this window now and return to the test script.</p>
                        </body>
                    </html>
                """)
            else:
                # Failed to receive the authorization code
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h1 style="color: #F44336;">Authentication failed!</h1>
                            <p>No authorization code received.</p>
                            <p>Please check the error message and try again.</p>
                            <p>Error details:</p>
                            <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto;">
                            """ + str(query_components).encode('utf-8') + b"""
                            </pre>
                        </body>
                    </html>
                """)
        else:
            # Any other path returns a 404
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging to keep console output clean."""
        return

def start_server():
    """Start a local HTTP server to receive the OAuth callback."""
    server = HTTPServer(('localhost', 5000), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

def get_auth_url():
    """
    Generate the authorization URL for the Microsoft OAuth flow.
    
    Returns:
        str: The authorization URL to open in the browser
    """
    base_url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/authorize"
    
    # Using the exact same scope format that worked in the main application
    scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
    
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": scope_string,
        "state": "12345"  # A random state value for CSRF protection
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return auth_url

def get_token_from_code(code):
    """
    Exchange the authorization code for an access token.
    
    Args:
        code (str): The authorization code received from the callback
        
    Returns:
        dict or None: The token data if successful, None if failed
    """
    token_url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
    
    # Using the exact same scope format that worked in the main application
    scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
    
    data = {
        "client_id": CLIENT_ID,
        "scope": scope_string,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": CLIENT_SECRET
    }
    
    print("Requesting token with params:", data)
    response = requests.post(token_url, data=data)
    
    if response.ok:
        print("Token response successful!")
        return response.json()
    else:
        print(f"Token request failed: {response.status_code}")
        print(response.text)
        return None

def test_graph_api(token):
    """
    Test Microsoft Graph API with the acquired token.
    
    This function tests three different endpoints to verify API access:
    1. /me - Basic user profile
    2. /me/messages - Email messages
    3. /me/mailFolders - Mail folders
    
    Args:
        token (str): The access token for API requests
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: User profile endpoint
    print("\n1. Testing /me endpoint...")
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        user_data = response.json()
        print(f"User: {user_data.get('displayName', 'Unknown')} ({user_data.get('userPrincipalName', 'Unknown')})")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Messages endpoint
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
    
    # Test 3: Mail folders endpoint
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
    """
    Main function to run the test script.
    
    This function orchestrates the entire OAuth flow and API testing process:
    1. Start a local server to receive the callback
    2. Open the authorization URL in the browser
    3. Wait for the user to authenticate and receive the callback
    4. Exchange the authorization code for an access token
    5. Test the Graph API with the access token
    """
    global auth_code, access_token, callback_received
    
    print(f"Starting Microsoft Graph API test using configuration from Config class...")
    print(f"Client ID: {CLIENT_ID[:5]}...{CLIENT_ID[-5:]} (masked for security)")
    
    # Validate required credentials are provided
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Client ID or Client Secret is missing in your Config.")
        return
    
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