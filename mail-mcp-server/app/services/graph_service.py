import requests
import json
import logging
from app.models.message import Message
from config import Config

logger = logging.getLogger(__name__)

class GraphService:
    """Service for interacting with Microsoft Graph API."""
    
    def __init__(self, access_token):
        self.access_token = access_token
        # Use v1.0 endpoint as shown in the documentation
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        logger.debug("GraphService initialized with token")
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the Microsoft Graph API."""
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making {method} request to {endpoint}")
        if params:
            logger.debug(f"Request params: {params}")
        if data:
            logger.debug(f"Request data: {json.dumps(data)[:100]}..." if data else "None")
        
        try:
            # Print full request details for debugging
            logger.debug(f"Full request: URL={url}, Headers={self.headers}, Params={params}, Data={data}")
            
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
                    raise Exception(f"Graph API error: {json.dumps(error_data)}")
                except json.JSONDecodeError:
                    logger.error(f"Non-JSON error response: {e.response.text}")
                    raise Exception(f"Graph API error: {e.response.text}")
            raise Exception(f"Request error: {str(e)}")
    
    def list_messages(self, skip=0, limit=10, filter_query=None, select_query=None, orderby=None, search=None):
        """
        Get a list of messages from the user's mailbox.
        
        Args:
            skip (int): Number of messages to skip for pagination
            limit (int): Maximum number of messages to return
            filter_query (str): OData filter query
            select_query (str): Properties to select
            orderby (str): Order results by specific properties
            search (str): Search query
            
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
    
    # Rest of the methods remain the same but with correct endpoint usage
    def get_message(self, message_id, select_query=None):
        """Get a specific message by ID."""
        params = {}
        if select_query:
            params['$select'] = select_query
        
        response = self._make_request('GET', f'/me/messages/{message_id}', params=params)
        return response
    
    def create_message(self, message_data):
        """Create a new message (draft)."""
        response = self._make_request('POST', '/me/messages', data=message_data)
        return response
    
    def update_message(self, message_id, update_data):
        """Update a specific message."""
        response = self._make_request('PATCH', f'/me/messages/{message_id}', data=update_data)
        if not response:
            response = self.get_message(message_id)
        return response
    
    def delete_message(self, message_id):
        """Delete a specific message."""
        self._make_request('DELETE', f'/me/messages/{message_id}')
    
    def send_message(self, message_id):
        """Send an existing draft message."""
        self._make_request('POST', f'/me/messages/{message_id}/send')
    
    def list_attachments(self, message_id):
        """Get a list of attachments for a specific message."""
        response = self._make_request('GET', f'/me/messages/{message_id}/attachments')
        return response
    
    def add_attachment(self, message_id, attachment_data):
        """Add an attachment to a specific message."""
        response = self._make_request('POST', f'/me/messages/{message_id}/attachments', data=attachment_data)
        return response
    
    def reply_to_message(self, message_id, reply_data):
        """Reply to a message."""
        self._make_request('POST', f'/me/messages/{message_id}/reply', data=reply_data)
    
    def reply_all_to_message(self, message_id, reply_data):
        """Reply all to a message."""
        self._make_request('POST', f'/me/messages/{message_id}/replyAll', data=reply_data)
    
    def forward_message(self, message_id, forward_data):
        """Forward a message."""
        self._make_request('POST', f'/me/messages/{message_id}/forward', data=forward_data)
    
    def send_mail(self, mail_data):
        """Send a new mail in a single operation."""
        self._make_request('POST', '/me/sendMail', data=mail_data)