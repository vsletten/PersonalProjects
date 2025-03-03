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
        self.base_url = Config.MS_GRAPH_API_ENDPOINT
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the Microsoft Graph API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            # Raise exception if request failed
            response.raise_for_status()
            
            # Return response data if not empty
            if response.content:
                return response.json()
            return None
            
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error making request to {url}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                error_data = e.response.json() if e.response.content else {"error": str(e)}
                raise Exception(f"Graph API error: {json.dumps(error_data)}")
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
        # Build query parameters
        params = {
            '$skip': skip,
            '$top': limit
        }
        
        if filter_query:
            params['$filter'] = filter_query
            
        if select_query:
            params['$select'] = select_query
            
        if orderby:
            params['$orderby'] = orderby
            
        if search:
            params['$search'] = search
        
        # Make request to Messages endpoint
        response = self._make_request('GET', '/me/messages', params=params)
        
        return response
    
    def get_message(self, message_id, select_query=None):
        """
        Get a specific message by ID.
        
        Args:
            message_id (str): ID of the message to retrieve
            select_query (str): Properties to select
            
        Returns:
            dict: Message data
        """
        # Build query parameters
        params = {}
        if select_query:
            params['$select'] = select_query
        
        # Make request to specific Message endpoint
        response = self._make_request('GET', f'/me/messages/{message_id}', params=params)
        
        return response
    
    def create_message(self, message_data):
        """
        Create a new message (draft).
        
        Args:
            message_data (dict): Message data
            
        Returns:
            dict: Created message data
        """
        # Make request to create a new message
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
        # Make request to update the message
        response = self._make_request('PATCH', f'/me/messages/{message_id}', data=update_data)
        
        # If no content is returned, get the updated message
        if not response:
            response = self.get_message(message_id)
            
        return response
    
    def delete_message(self, message_id):
        """
        Delete a specific message.
        
        Args:
            message_id (str): ID of the message to delete
        """
        # Make request to delete the message
        self._make_request('DELETE', f'/me/messages/{message_id}')
    
    def send_message(self, message_id):
        """
        Send an existing draft message.
        
        Args:
            message_id (str): ID of the message to send
        """
        # Make request to send the message
        self._make_request('POST', f'/me/messages/{message_id}/send')
    
    def list_attachments(self, message_id):
        """
        Get a list of attachments for a specific message.
        
        Args:
            message_id (str): ID of the message
            
        Returns:
            dict: Attachments listing
        """
        # Make request to get attachments
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
        # Make request to add attachment
        response = self._make_request('POST', f'/me/messages/{message_id}/attachments', data=attachment_data)
        
        return response
    
    def move_message(self, message_id, destination_folder_id):
        """
        Move a message to another folder.
        
        Args:
            message_id (str): ID of the message to move
            destination_folder_id (str): ID of the destination folder
            
        Returns:
            dict: Moved message data
        """
        # Prepare the move data
        move_data = {
            "destinationId": destination_folder_id
        }
        
        # Make request to move the message
        response = self._make_request('POST', f'/me/messages/{message_id}/move', data=move_data)
        
        return response
    
    def copy_message(self, message_id, destination_folder_id):
        """
        Copy a message to another folder.
        
        Args:
            message_id (str): ID of the message to copy
            destination_folder_id (str): ID of the destination folder
            
        Returns:
            dict: Copied message data
        """
        # Prepare the copy data
        copy_data = {
            "destinationId": destination_folder_id
        }
        
        # Make request to copy the message
        response = self._make_request('POST', f'/me/messages/{message_id}/copy', data=copy_data)
        
        return response
    
    def reply_to_message(self, message_id, reply_data):
        """
        Reply to a message.
        
        Args:
            message_id (str): ID of the message to reply to
            reply_data (dict): Reply data
        """
        # Make request to reply to the message
        self._make_request('POST', f'/me/messages/{message_id}/reply', data=reply_data)
    
    def reply_all_to_message(self, message_id, reply_data):
        """
        Reply all to a message.
        
        Args:
            message_id (str): ID of the message to reply to
            reply_data (dict): Reply data
        """
        # Make request to reply all to the message
        self._make_request('POST', f'/me/messages/{message_id}/replyAll', data=reply_data)
    
    def forward_message(self, message_id, forward_data):
        """
        Forward a message.
        
        Args:
            message_id (str): ID of the message to forward
            forward_data (dict): Forward data
        """
        # Make request to forward the message
        self._make_request('POST', f'/me/messages/{message_id}/forward', data=forward_data)
        
    def create_draft(self, draft_data):
        """
        Create a draft message.
        
        Args:
            draft_data (dict): Draft message data
            
        Returns:
            dict: Created draft message data
        """
        # Make request to create a draft message
        response = self._make_request('POST', '/me/messages', data=draft_data)
        
        return response
        
    def send_mail(self, mail_data):
        """
        Create and send a new message in a single operation.
        
        Args:
            mail_data (dict): Message data
        """
        # Make request to send a new message
        self._make_request('POST', '/me/sendMail', data=mail_data)
        
    def get_message_extensions(self, message_id):
        """
        Get open extensions for a message.
        
        Args:
            message_id (str): ID of the message
            
        Returns:
            dict: Message extensions
        """
        # Make request to get extensions
        response = self._make_request('GET', f'/me/messages/{message_id}/extensions')
        
        return response
        
    def add_message_extension(self, message_id, extension_data):
        """
        Add an open extension to a message.
        
        Args:
            message_id (str): ID of the message
            extension_data (dict): Extension data
            
        Returns:
            dict: Added extension data
        """
        # Make request to add extension
        response = self._make_request('POST', f'/me/messages/{message_id}/extensions', data=extension_data)
        
        return response
    
    # Note: Only implementing message endpoint operations as requested.