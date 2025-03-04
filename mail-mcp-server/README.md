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

4. **404 Errors on API Endpoints**:
   - Verify URL path matches the blueprint registration
   - Check if the Flask server is running on the expected port
   - Ensure the route handler is correctly implemented

5. **Permission Denied Errors**:
   - Review the permissions granted in Azure AD
   - Make sure admin consent has been provided if required
   - Check scope formatting in oauth.py

### Debugging Tips

1. **Enable Debug Logging**:
   - Set `LOG_LEVEL=DEBUG` in your .env file
   - Check console output for detailed request/response logs

2. **Use the Test Script**:
   - Run `test_graph_api.py` to verify your Azure configuration independently
   - Helps isolate whether issues are with Azure configuration or your application

3. **Check Token Information**:
   - Visit `/auth/token-info` endpoint after authentication
   - Verify scopes and expiration time

4. **Browser Developer Tools**:
   - Monitor network requests to identify where issues occur
   - Check for CORS errors or failed network requests

5. **Microsoft Graph Explorer**:
   - Use [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) to test API requests
   - Helps determine if issues are specific to your application or API-wide

## Advanced Usage

### Filtering Messages

The `/api/messages` endpoint supports OData filtering:

```
GET /api/messages?filter=isRead eq false
```

Common filter examples:
- `isRead eq false` - Unread messages only
- `importance eq 'high'` - High importance messages
- `receivedDateTime ge 2023-01-01T00:00:00Z` - Messages received after January 1, 2023

### Pagination

To handle large mailboxes, use the skip and limit parameters:

```
GET /api/messages?skip=0&limit=10
```

Then get the next page:

```
GET /api/messages?skip=10&limit=10
```

### Selecting Specific Fields

To optimize response size, specify only the fields you need:

```
GET /api/messages?select=subject,from,receivedDateTime
```

### Search

Full-text search across messages:

```
GET /api/messages?search="meeting agenda"
```

## Rate Limiting

Microsoft Graph API has rate limits that apply to your application. Consider implementing:

1. Request throttling
2. Exponential backoff for retries
3. Caching frequently accessed data

See [Microsoft's documentation on throttling](https://docs.microsoft.com/en-us/graph/throttling) for details.

## Security Considerations

1. **Store Secrets Securely**:
   - Never commit .env files to source control
   - Use a secrets manager in production

2. **HTTPS in Production**:
   - Always use HTTPS for production deployments
   - Configure Flask with a proper WSGI server like Gunicorn or uWSGI

3. **Minimize Token Exposure**:
   - Don't expose tokens to client-side code
   - Store tokens in server-side sessions only

4. **Authorization**:
   - Implement proper user authorization if multiple users access the application
   - Consider using a proper authentication middleware

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Microsoft Graph API documentation
- Flask documentation
- Contributors to the MSAL Python library

## Support

For questions or issues, please open an issue on the GitHub repository or contact the maintainers directly.