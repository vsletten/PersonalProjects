from datetime import datetime
from typing import Dict, List, Optional, Union, Any

class Message:
    """
    Class representing a Microsoft Graph API message.
    
    This class provides a Pythonic interface to work with the properties of an email
    message from the Microsoft Graph API. It allows for creating message objects
    from API responses and converting message objects to dictionaries for API requests.
    
    Attributes:
        id (str): Unique identifier for the message
        subject (str): Subject line of the message
        body (dict): Body content of the message (contains contentType and content)
        from_value (dict): Sender information
        sender (dict): Sender information (may differ from from_value in some cases)
        to_recipients (list): List of primary recipients
        cc_recipients (list): List of CC recipients
        bcc_recipients (list): List of BCC recipients
        created_datetime (str): ISO datetime when the message was created
        last_modified_datetime (str): ISO datetime when the message was last modified
        received_datetime (str): ISO datetime when the message was received
        sent_datetime (str): ISO datetime when the message was sent
        has_attachments (bool): Whether the message has attachments
        importance (str): Importance level of the message (low, normal, high)
        is_read (bool): Whether the message has been read
        categories (list): List of categories assigned to the message
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize a Message object from keyword arguments.
        
        The constructor accepts a dictionary of properties, typically from a Graph API
        response, and maps them to Python-friendly attribute names.
        
        Args:
            **kwargs: Arbitrary keyword arguments representing message properties
        """
        self.id = kwargs.get('id')
        self.subject = kwargs.get('subject')
        self.body = kwargs.get('body')
        self.from_value = kwargs.get('from')  # 'from' is a reserved word in Python
        self.sender = kwargs.get('sender')
        self.to_recipients = kwargs.get('toRecipients', [])
        self.cc_recipients = kwargs.get('ccRecipients', [])
        self.bcc_recipients = kwargs.get('bccRecipients', [])
        self.created_datetime = kwargs.get('createdDateTime')
        self.last_modified_datetime = kwargs.get('lastModifiedDateTime')
        self.received_datetime = kwargs.get('receivedDateTime')
        self.sent_datetime = kwargs.get('sentDateTime')
        self.has_attachments = kwargs.get('hasAttachments', False)
        self.importance = kwargs.get('importance', 'normal')
        self.is_read = kwargs.get('isRead', False)
        self.categories = kwargs.get('categories', [])
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Message object to dictionary for API responses.
        
        This method creates a dictionary suitable for JSON serialization and use in
        Graph API requests. It converts Python-friendly attribute names back to the
        names expected by the Graph API and removes any None values.
        
        Returns:
            dict: Message data as a dictionary with Graph API property names
        """
        message_dict = {
            'id': self.id,
            'subject': self.subject,
            'body': self.body,
            'from': self.from_value,  # Convert back to 'from' for API
            'sender': self.sender,
            'toRecipients': self.to_recipients,
            'ccRecipients': self.cc_recipients,
            'bccRecipients': self.bcc_recipients,
            'createdDateTime': self.created_datetime,
            'lastModifiedDateTime': self.last_modified_datetime,
            'receivedDateTime': self.received_datetime,
            'sentDateTime': self.sent_datetime,
            'hasAttachments': self.has_attachments,
            'importance': self.importance,
            'isRead': self.is_read,
            'categories': self.categories
        }
        
        # Remove None values to avoid sending null properties to the API
        return {k: v for k, v in message_dict.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a Message object from a dictionary.
        
        This is a factory method that creates a new Message instance from a dictionary,
        typically from a Graph API response.
        
        Args:
            data (dict): Dictionary containing message properties
            
        Returns:
            Message: A new Message instance
        """
        return cls(**data)
        
    def __str__(self) -> str:
        """
        Return a string representation of the message.
        
        Returns:
            str: A string with the message subject and ID
        """
        return f"Message(subject='{self.subject}', id='{self.id}')"
        
    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the message.
        
        Returns:
            str: A string suitable for debugging
        """
        return f"Message(id='{self.id}', subject='{self.subject}', is_read={self.is_read})"