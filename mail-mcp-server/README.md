# Microsoft Graph API MCP Server

A complete Message Consumer Protocol (MCP) server providing a RESTful interface to the Microsoft Graph API for email messages. This server supports all operations including reading, creating, updating, sending, and deleting email messages through Microsoft's Graph API.

## Features

- Full CRUD operations for Microsoft Graph API messages endpoint
- Authentication with Microsoft OAuth 2.0
- Pagination support for message listings
- Filtering and search capabilities
- Attachment handling
- Message reply/forward operations
- Token refresh handling
- Comprehensive error handling

## Prerequisites

- Python 3.8+
- Microsoft Azure Account with:
  - Registered application in Azure AD
  - Required permissions configured
  - Client ID and Client Secret
- Microsoft account with a mailbox (personal or work/school account)

## Getting Started

### 1. Azure Application Registration

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory > App registrations
3. Click "New registration"
4. Enter a name for your application
5. Select the appropriate account type:
   - For personal Microsoft accounts, select "Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)"
6. Add a redirect URI:
   - Type: Web
   - URL: `http://localhost:5000/auth/callback`
7. Click "Register"

### 2. Configure API Permissions

1. In your newly registered app, go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph"
4. Choose "Delegated permissions"
5. Add the following permissions:
   - Mail.ReadWrite
   - Mail.Send
   - User.Read
   - offline_access
6. Click "Add permissions"
7. Click "Grant admin consent" (if you're an admin)

### 3. Create a Client Secret

1. In your app registration, go to "Certificates & secrets"
2. Click "New client secret"
3. Enter a description and select expiration
4. Click "Add"
5. **Important**: Copy the secret value immediately, as you won't be able to see it again

### 4. Configure Authentication

1. In your app registration, go to "Authentication"
2. Under "Implicit grant and hybrid flows", check "Access tokens"
3. Click "Save"

### 5. Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Azure configurations:
   ```
   MS_CLIENT_ID=your_client_id
   MS_CLIENT_SECRET=your_client_secret
   MS_TENANT_ID=common  # Use 'common' for personal accounts
   MS_REDIRECT_URI=http://localhost:5000/auth/callback
   SECRET_KEY=generate_a_strong_random_secret_key
   LOG_LEVEL=INFO
   ```
5. Run the server:
   ```bash
   python run.py
   ```

### 6. Testing your Configuration

To verify your Azure application configuration and Graph API access, you can use the included test script:

1. Open `test_graph_api.py`
2. Fill in your Client ID and Client Secret at the top of the file
3. Run the script:
   ```bash
   python test_graph_api.py
   ```
4. Follow the browser prompts to authenticate
5. The script will test your access to various Graph API endpoints

## API Endpoints

### Authentication

- **GET /auth/login** - Start OAuth flow
- **GET /auth/callback** - OAuth callback from Microsoft
- **GET /auth/logout** - Log out user
- **GET /auth/status** - Check authentication status
- **GET /auth/token-info** - View token information (debug endpoint)
- **GET /auth/debug-me** - User profile and mailbox info (debug endpoint)

### Messages

- **GET /api/messages** - List messages
  - Query params: skip, limit, filter, select, orderby, search
- **GET /api/messages/{id}** - Get a specific message
  - Query params: select
- **POST /api/messages** - Create a draft message
- **PATCH /api/messages/{id}** - Update a message
- **DELETE /api/messages/{id}** - Delete a message
- **POST /api/messages/{id}/send** - Send a draft message
- **POST /api/messages/{id}/reply** - Reply to a message
- **POST /api/messages/{id}/replyAll** - Reply all to a message
- **POST /api/messages/{id}/forward** - Forward a message
- **GET /api/messages/{id}/attachments** - Get message attachments
- **POST /api/messages/{id}/attachments** - Add an attachment to a message
- **POST /api/sendMail** - Send a new mail in one operation

## Project Structure

```
mcp-graph-server/
├── app/
│   ├── __init__.py         # Flask application factory
│   ├── auth/
│   │   ├── __init__.py
│   │   └── oauth.py        # OAuth authentication
│   ├── models/
│   │   ├── __init__.py
│   │   └── message.py      # Message data model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py  # Authentication endpoints
│   │   └── message_routes.py  # Message API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── graph_service.py   # Graph API service
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Utility functions
├── config.py               # Application configuration
├── run.py                  # Application entry point
├── test_graph_api.py       # Standalone test script
├── requirements.txt        # Dependencies
├── setup.py                # Package configuration
└── .env                    # Environment variables
```

## Creating an Email Message

To create a draft email message, send a POST request to `/api/messages` with the following JSON structure:

```json
{
  "subject": "Meeting tomorrow",
  "body": {
    "contentType": "html",
    "content": "<p>Hello,</p><p>Let's meet tomorrow at 10 AM.</p>"
  },
  "toRecipients": [
    {
      "emailAddress": {
        "name": "John Doe",
        "address": "john@example.com"
      }
    }
  ]
}
```

To send the message immediately, use the `/api/sendMail` endpoint with:

```json
{
  "message": {
    "subject": "Meeting tomorrow",
    "body": {
      "contentType": "html",
      "content": "<p>Hello,</p><p>Let's meet tomorrow at 10 AM.</p>"
    },
    "toRecipients": [
      {
        "emailAddress": {
          "name": "John Doe",
          "address": "john@example.com"
        }
      }
    ]
  },
  "saveToSentItems": true
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Check your client ID and secret
   - Verify the redirect URI matches exactly in Azure and .env
   - Ensure you've granted the required permissions

2. **"MailboxNotEnabledForRESTAPI" Error**:
   - This usually means your account doesn't have a mailbox accessible via the REST API
   - Verify you're using an Office 365 account with Exchange Online
   - Personal accounts may have limited functionality

3. **Token Refresh Issues**:
   - Make sure `offline_access` permission is included
   - Check session configuration in Flask

4. **404 Errors on