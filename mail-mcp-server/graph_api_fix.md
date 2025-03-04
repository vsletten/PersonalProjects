# Fixing Microsoft Graph API Implementation

Based on the official Microsoft documentation, here are the key issues identified and their solutions:

## 1. Authentication Flow Issues

The OAuth 2.0 authentication flow must follow these exact steps:

1. **Step 1: Request authorization with correct scopes**
   - Use the `/authorize` endpoint with properly formatted scope strings
   - Use the correct tenant (use `common` for both personal and work accounts)
   - Use exact permission URIs (not shorthand names)

2. **Step 2: Exchange code for token**
   - Use the same scope string as in Step 1
   - Include all required parameters

3. **Step 3: Use the token to call Microsoft Graph**
   - Use the correct base URL: `https://graph.microsoft.com/v1.0`
   - Include the token as a Bearer token in the Authorization header

## Key Implementation Changes

### 1. Use the correct scope format

```python
# WRONG
scope = "Mail.ReadWrite Mail.Send offline_access"

# CORRECT 
scope = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
```

### 2. Use the correct tenant identifier

For personal Microsoft accounts, use `common` or `consumers` instead of a specific tenant ID:

```python
# WRONG (for personal accounts)
base_url = f"https://login.microsoftonline.com/{Config.MS_TENANT_ID}/oauth2/v2.0/authorize"

# CORRECT (for personal accounts)
base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
```

### 3. Request the offline_access scope

Always include the `offline_access` scope to get refresh tokens:

```python
scope_string = "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/User.Read offline_access"
```

### 4. Use the v1.0 endpoint for API calls

```python
# WRONG
self.base_url = "https://graph.microsoft.com/beta"

# CORRECT
self.base_url = "https://graph.microsoft.com/v1.0"
```

## Implementation Steps

1. Replace the `oauth.py` file with the corrected implementation.
2. Replace or update the `graph_service.py` file to use the correct endpoint.
3. Make sure all __init__.py files exist and are properly importing the required modules.
4. Clear all browser cookies and session data.
5. Run the standalone test script to verify the token flow.
6. Finally, restart your Flask application with the corrected implementation.

## Verification Steps

After making these changes, you should:

1. Test authentication by visiting `/auth/login`
2. Check the token info at `/auth/token-info` to verify the scopes
3. Try listing messages at `/api/messages`

## Common Error Causes

1. **Incorrect scope format**: Scopes must be full URIs
2. **Missing necessary scopes**: User.Read is often required
3. **Wrong tenant value**: Must use 'common' for personal accounts
4. **Session issues**: Flask-Session configuration problems
5. **Redirect URI mismatch**: Must exactly match what's registered in Azure

These changes should resolve the "MailboxNotEnabledForRESTAPI" error by properly implementing the OAuth flow according to Microsoft's documentation.