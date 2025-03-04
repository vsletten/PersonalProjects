import requests
import json
import logging
from app.models.message import Message
from config import Config

logger = logging.getLogger(__name__)

class GraphService:
    """
    Service for interacting with Microsoft Graph API.
    
    This class provides methods for various operations on Microsoft Graph API
    resources, with a focus on email message-related endpoints.
    
    Attributes:
        access_token (str): The OAuth access token for authenticating with Graph API
        base_url (str): The base URL for the Graph API
        headers (dict): Headers to include in all API requests
    """
    
    def __init__(self, access_token):
        """
        Initialize the GraphService with an access token.
        
        Args:
            access_token (str): The OAuth access token for Microsoft Graph API
        """
        self.access_token = access_token
        # Use v1.0 endpoint as shown in the documentation
        # The v1.0 endpoint is stable and recommended for production use
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        logger.debug("GraphService initialized with token")
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Make a request to the Microsoft Graph API.
        
        This is a generic method for making HTTP requests to any Graph API endpoint.
        It handles error responses and logging.
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint path (starts with /)
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            
        Returns:
            dict or None: Response data as dictionary or None for empty responses
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making {method} request to {endpoint}")
        if params:
            logger.debug(f"Request params: {params}")
        if data:
            logger.debug(f"Request data: {json.dumps(data)[:100]}..." if data else "None")
        
        try:
            # Print full request details for debugging (omitting sensitive headers)
            debug_headers = {k: v for k, v in self.headers.items() if k != 'Authorization'}
            logger.debug(f"Request details: URL={url}, Headers={debug_headers}, Params={params}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            logger.debug(f"Response status: {response.status_code}")
            if not response.ok:
                logger.warning(f"Error response: {response.text[:200]}...")
            
            # Raise exception if request failed
            response.raise_for_status()
            
            # Return response data if not empty
            if response.content:
                logger.debug(f"Response length: {len(response.content)} bytes")
                return response.json()
            logger.debug("Empty response content")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error making request to {url}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json() if e.response.content else {"error": str(e)}
                    logger.error(f"Graph API error response: {json.dumps(error_data)}")
                    
                    # Check for specific error codes and provide better error messages
                    if 'error' in error_data and 'code' in error_data['error']:
                        error_code = error_data['error']['code']
                        
                        if error_code == 'AuthenticationError':
                            raise Exception("Authentication failed. Your token may have expired.")
                        elif error_code == 'MailboxNotEnabledForRESTAPI':
                            raise Exception("This mailbox is not enabled for Graph API access. Make sure you're using an Office 365 account with Exchange Online.")
                        elif error_code == 'AccessDenied':
                            raise Exception("Access denied. Your application may not have the required permissions.")
                        else:
                            raise Exception(f"Graph API error: {json.dumps(error_data)}")
                    else:
                        raise Exception(f"Graph API error: {json.dumps(error_data)}")
                    
                except json.JSONDecodeError:
                    logger.error(f"Non-JSON error response: {e.response.text}")
                    raise Exception(f"Graph API error: {e.response.text}")
            raise Exception(f"Request error: {str(e)}")
    
    def list_messages(self, skip=0, limit=10, filter_query=None, select_query=None, orderby=None, search=None):
        """
        Get a list of messages from the user's mailbox.
        
        This method retrieves a paginated list of messages with optional filtering,
        sorting, and search capabilities.
        
        Args:
            skip (int, optional): Number of messages to skip for pagination
            limit (int, optional): Maximum number of messages to return
            filter_query (str, optional): OData filter query (e.g., "isRead eq false")
            select_query (str, optional): Properties to select (e.g., "subject,from,receivedDateTime")
            orderby (str, optional): Order results by specific properties (e.g., "receivedDateTime desc")
            search (str, optional): Search query for searching message content
            
        Returns:
            dict: Messages listing with pagination info
        """
        logger.info(f"Listing messages: skip={skip}, limit={limit}")
        
        # Build query parameters
        params = {}
        
        if skip is not None:
            params['$skip'] = skip
            
        if limit is not None:
            params['$top'] = limit
            
        if filter_query:
            params['$filter'] = filter_query
            
        if select_query:
            params['$select'] = select_query
            
        if orderby:
            params['$orderby'] = orderby
            
        if search:
            params['$search'] = search
        
        # Make request to Messages endpoint as shown in the documentation
        response = self._make_request('GET', '/me/messages', params=params)
        logger.info(f"Successfully retrieved messages")
        return response
    
    def get_message(self, message_id, select_query=None):
        """
        Get a specific message by ID.
        
        Args:
            message_id (str): ID of the message to retrieve
            select_query (str, optional): Properties to select
            
        Returns:
            dict: Message data
        """
        params = {}
        if select_query:
            params['$select'] = select_query
        
        response = self._make_request('GET', f'/me/messages/{message_id}', params=params)
        return response
    
    def create_message(self, message_data):
        """
        Create a new message (draft).
        
        This creates a draft message in the user's mailbox but does not send it.
        Use send_message() to send a draft message.
        
        Args:
            message_data (dict): Message data including subject, body, recipients, etc.
            
        Returns:
            dict: Created message data
        """
        response = self._make_request('POST', '/me/messages', data=message_data)
        return response
    
    def update_message(self, message_id, update_data):
        """
        Update a specific message.
        
        Args:
            message_id (str): ID of the message to update
            update_data (dict): Updated message data
            
        Returns:
            dict: Updated message data
        """
        response = self._make_request('PATCH', f'/me/messages/{message_id}', data=update_data)
        if not response:
            response = self.get_message(message_id)
        return response
    
    def delete_message(self, message_id):
        """
        Delete a specific message.
        
        Args:
            message_id (str): ID of the message to delete
        """
        self._make_request('DELETE', f'/me/messages/{message_id}')
    
    def send_message(self, message_id):
        """
        Send an existing draft message.
        
        Args:
            message_id (str): ID of the draft message to send
        """
        self._make_request('POST', f'/me/messages/{message_id}/send')
    
    def list_attachments(self, message_id):
        """
        Get a list of attachments for a specific message.
        
        Args:
            message_id (str): ID of the message
            
        Returns:
            dict: Attachments listing
        """
        response = self._make_request('GET', f'/me/messages/{message_id}/attachments')
        return response
    
    def add_attachment(self, message_id, attachment_data):
        """
        Add an attachment to a specific message.
        
        Args:
            message_id (str): ID of the message
            attachment_data (dict): Attachment data
            
        Returns:
            dict: Added attachment data
        """
        response = self._make_request('POST', f'/me/messages/{message_id}/attachments', data=attachment_data)
        return response
    
    def reply_to_message(self, message_id, reply_data):
        """
        Reply to a message.
        
        Args:
            message_id (str): ID of the message to reply to
            reply_data (dict): Reply data including message content
        """
        self._make_request('POST', f'/me/messages/{message_id}/reply', data=reply_data)
    
    def reply_all_to_message(self, message_id, reply_data):
        """
        Reply all to a message.
        
        Args:
            message_id (str): ID of the message to reply to
            reply_data (dict): Reply data including message content
        """
        self._make_request('POST', f'/me/messages/{message_id}/replyAll', data=reply_data)
    
    def forward_message(self, message_id, forward_data):
        """
        Forward a message.
        
        Args:
            message_id (str): ID of the message to forward
            forward_data (dict): Forward data including recipient and optional comment
        """
        self._make_request('POST', f'/me/messages/{message_id}/forward', data=forward_data)
    
    def send_mail(self, mail_data):
        """
        Send a new mail in a single operation.
        
        This is a convenience method that creates and sends a message in one step.
        
        Args:
            mail_data (dict): Message data with required fields:
                - message: The message object with subject, body, toRecipients
                - saveToSentItems (bool): Whether to save to sent items folder
        """
        self._make_request('POST', '/me/sendMail', data=mail_data)