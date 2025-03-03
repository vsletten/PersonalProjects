# MCP Server for Microsoft Graph API Messages

This MCP (Message Consumer Protocol) server provides a complete interface to the Microsoft Graph API messages endpoint. It supports all operations including reading, creating, updating, and deleting email messages.

## Features

- Full CRUD operations for Microsoft Graph API messages endpoint
- Authentication with Microsoft OAuth 2.0
- Pagination support for message listings
- Filtering and search capabilities
- Attachment handling
- Message reply/forward operations

## Prerequisites

- Python 3.8+
- Microsoft Azure Application registration with the following configurations:
  - Registered application in Azure AD
  - Configured redirect URI: `http://localhost:5000/auth/callback`
  - Delegated permissions: `Mail.ReadWrite`, `Mail.Send`, `User.Read`, `offline_access`
  - Admin consent granted (if required by your tenant)
- Microsoft 365 account with an Exchange Online mailbox

## Installation

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
4. Copy `.env.example` to `.env` and fill in your Microsoft Graph API credentials
5. Run the server:
   ```bash
   python run.py
   ```

## Configuration

Edit the `.env` file with your Microsoft Graph API client credentials:

```
MS_CLIENT_ID=your_client_id
MS_CLIENT_SECRET=your_client_secret
MS_TENANT_ID=your_tenant_id
MS_REDIRECT_URI=http://localhost:5000/auth/callback
SECRET_KEY=your_secret_key
```

## Usage

The server exposes REST endpoints that map to Microsoft Graph API message operations:

### Authentication Endpoints

- `GET /auth/login` - Start OAuth login flow
- `GET /auth/callback` - OAuth callback from Microsoft
- `GET /auth/logout` - Log out user
- `GET /auth/status` - Check authentication status
- `GET /auth/token-info` - View token information (scopes, expiration)
- `GET /auth/debug-me` - Debug endpoint to check user profile and mailbox access

### Message API Endpoints

- `GET /api/messages` - List messages
- `GET /api/messages/{id}` - Get a specific message
- `POST /api/messages` - Create a new message
- `PATCH /api/messages/{id}` - Update a message
- `DELETE /api/messages/{id}` - Delete a message
- `POST /api/messages/{id}/send` - Send a draft message
- `POST /api/messages/{id}/reply` - Reply to a message
- `POST /api/messages/{id}/replyAll` - Reply all to a message
- `POST /api/messages/{id}/forward` - Forward a message
- `GET /api/messages/{id}/attachments` - Get message attachments
- `POST /api/messages/{id}/attachments` - Add an attachment to a message

## Authentication Flow

1. Visit the home page (`/`)
2. Click "Login" to start the authentication flow
3. You'll be redirected to Microsoft's login page
4. After authentication, Microsoft will redirect back to your application
5. The application will exchange the authorization code for an access token
6. You can now use the API endpoints

## Troubleshooting

If you encounter the error `MailboxNotEnabledForRESTAPI`, please check:

1. Your Microsoft account must be a Microsoft 365/Office 365 account with Exchange Online
2. Personal Microsoft accounts (outlook.com, hotmail.com, etc.) may not work
3. Verify your Azure AD application has the correct permissions and admin consent
4. Check the debug endpoints for more information:
   - `/auth/token-info` - View token scopes
   - `/auth/debug-me` - Test user profile and mailbox access

See the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for more detailed steps.

## License

MIT