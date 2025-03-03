from datetime import datetime
from typing import Dict, List, Optional, Union, Any

class Message:
    """
    Class representing a Microsoft Graph API message.
    """
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.subject = kwargs.get('subject')
        self.body = kwargs.get('body')
        self.from_value = kwargs.get('from')
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
        """
        message_dict = {
            'id': self.id,
            'subject': self.subject,
            'body': self.body,
            'from': self.from_value,
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
        
        # Remove None values
        return {k: v for k, v in message_dict.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a Message object from a dictionary.
        """
        return cls(**data)
