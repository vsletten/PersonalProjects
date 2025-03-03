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
- Microsoft Azure Application registration (for API access)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Microsoft Graph API credentials
4. Run the server:
   ```
   python run.py
   ```

## Configuration

Edit the `.env` file with your Microsoft Graph API client credentials:

```
MS_CLIENT_ID=your_client_id
MS_CLIENT_SECRET=your_client_secret
MS_TENANT_ID=your_tenant_id
MS_REDIRECT_URI=http://localhost:5000/auth/callback
```

## Usage

The server exposes REST endpoints that map to Microsoft Graph API message operations:

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

## Authentication

The server implements Microsoft OAuth 2.0 authentication flow:

1. Visit `/auth/login` to start the authentication flow
2. Microsoft will redirect back to `/auth/callback` after authentication
3. Check authentication status at `/auth/status`
4. Logout with `/auth/logout`

## API Examples

### List messages
```
GET /api/messages?limit=25&filter=isRead eq false
```

### Create a new message
```
POST /api/messages
Content-Type: application/json

{
  "subject": "Hello from MCP server",
  "body": {
    "contentType": "html",
    "content": "<p>This is a test message.</p>"
  },
  "toRecipients": [
    {
      "emailAddress": {
        "name": "John Doe",
        "address": "john.doe@example.com"
      }
    }
  ]
}
```

### Update a message
```
PATCH /api/messages/{message_id}
Content-Type: application/json

{
  "subject": "Updated subject line"
}
```

## License

MIT
