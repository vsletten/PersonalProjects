import base64
import json
import logging
from typing import List, Dict, Any, Union, Optional, Tuple

logger = logging.getLogger(__name__)

def encode_attachment_content(file_content: bytes) -> str:
    """
    Encode file content to base64 for attachment.
    
    Microsoft Graph API requires file attachments to be base64 encoded.
    This function converts binary file content to a base64 encoded string.
    
    Args:
        file_content (bytes): File content as bytes
        
    Returns:
        str: Base64 encoded file content as a string
        
    Raises:
        Exception: If encoding fails
    """
    try:
        encoded = base64.b64encode(file_content).decode('utf-8')
        return encoded
    except Exception as e:
        logger.exception(f"Error encoding attachment content: {str(e)}")
        raise Exception(f"Failed to encode attachment: {str(e)}")

def decode_attachment_content(base64_content: str) -> bytes:
    """
    Decode base64 content from attachment.
    
    This function converts a base64 encoded string back to binary data,
    useful for processing attachments received from the Graph API.
    
    Args:
        base64_content (str): Base64 encoded content
        
    Returns:
        bytes: Decoded file content as bytes
        
    Raises:
        Exception: If decoding fails
    """
    try:
        decoded = base64.b64decode(base64_content)
        return decoded
    except Exception as e:
        logger.exception(f"Error decoding attachment content: {str(e)}")
        raise Exception(f"Failed to decode attachment: {str(e)}")

def format_email_address(name: str, address: str) -> Dict[str, Dict[str, str]]:
    """
    Format email address for Microsoft Graph API.
    
    Microsoft Graph API requires email addresses to be formatted in a specific way.
    This function creates the proper structure for an email address.
    
    Args:
        name (str): Display name of the recipient
        address (str): Email address of the recipient
        
    Returns:
        dict: Formatted email address in the structure expected by Graph API
    """
    return {
        "emailAddress": {
            "name": name,
            "address": address
        }
    }

def create_recipient_list(recipients: List[Dict[str, str]]) -> List[Dict[str, Dict[str, str]]]:
    """
    Create a list of recipients in the correct format for Graph API.
    
    Takes a simple list of recipients with name and address keys and
    converts it to the proper format expected by Microsoft Graph API.
    
    Args:
        recipients (list): List of dicts with 'name' and 'address' keys
        
    Returns:
        list: List of formatted recipients for Graph API
        
    Example:
        >>> create_recipient_list([{'name': 'John Doe', 'address': 'john@example.com'}])
        [{'emailAddress': {'name': 'John Doe', 'address': 'john@example.com'}}]
    """
    formatted_recipients = []
    
    for recipient in recipients:
        formatted_recipients.append(format_email_address(
            recipient.get('name', ''),
            recipient.get('address', '')
        ))
    
    return formatted_recipients

def create_message_body(content: str, content_type: str = 'html') -> Dict[str, str]:
    """
    Create a message body in the correct format for Graph API.
    
    Microsoft Graph API requires message bodies to have a specific structure
    with contentType (html or text) and the actual content.
    
    Args:
        content (str): Message content (HTML markup or plain text)
        content_type (str): Content type ('html' or 'text')
        
    Returns:
        dict: Formatted message body for Graph API
        
    Example:
        >>> create_message_body('<p>Hello world</p>', 'html')
        {'contentType': 'html', 'content': '<p>Hello world</p>'}
    """
    # Validate content_type
    if content_type not in ['html', 'text']:
        logger.warning(f"Invalid content_type '{content_type}', defaulting to 'html'")
        content_type = 'html'
        
    return {
        "contentType": content_type,
        "content": content
    }

def create_file_attachment(name: str, content_bytes: bytes, content_type: str) -> Dict[str, str]:
    """
    Create a file attachment in the correct format for Graph API.
    
    Microsoft Graph API requires file attachments to be formatted with specific
    properties and base64 encoded content.
    
    Args:
        name (str): File name
        content_bytes (bytes): File content as bytes
        content_type (str): MIME type of the file
        
    Returns:
        dict: Formatted file attachment for Graph API
        
    Example:
        >>> with open('document.pdf', 'rb') as f:
        ...     attachment = create_file_attachment('document.pdf', f.read(), 'application/pdf')
    """
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": name,
        "contentType": content_type,
        "contentBytes": encode_attachment_content(content_bytes)
    }

def parse_odata_next_link(next_link: Optional[str]) -> Optional[str]:
    """
    Parse OData next link to extract skip token.
    
    Microsoft Graph API uses OData for paging. This function extracts the
    skiptoken parameter from a nextLink URL, which can be used for pagination.
    
    Args:
        next_link (str): OData next link URL
        
    Returns:
        str or None: Skip token if found, None otherwise
        
    Example:
        >>> parse_odata_next_link('https://graph.microsoft.com/v1.0/me/messages?$skiptoken=abc123')
        'abc123'
    """
    if not next_link:
        return None
        
    # Find the skiptoken parameter
    if "$skiptoken=" in next_link:
        parts = next_link.split("$skiptoken=")
        if len(parts) > 1:
            # Get the skiptoken value and remove any trailing parameters
            return parts[1].split("&")[0]
    
    return None

def create_draft_email(subject: str, body: str, to_recipients: List[Dict[str, str]], 
                      cc_recipients: Optional[List[Dict[str, str]]] = None,
                      bcc_recipients: Optional[List[Dict[str, str]]] = None,
                      body_type: str = 'html') -> Dict[str, Any]:
    """
    Create a draft email message in the format required by Graph API.
    
    This is a helper function that combines multiple helpers to create a complete
    message object for creating a draft email.
    
    Args:
        subject (str): Email subject
        body (str): Email body content
        to_recipients (list): List of dictionaries with 'name' and 'address' keys
        cc_recipients (list, optional): List of CC recipients
        bcc_recipients (list, optional): List of BCC recipients
        body_type (str, optional): Body content type ('html' or 'text')
        
    Returns:
        dict: Complete message object for Graph API
    """
    message = {
        "subject": subject,
        "body": create_message_body(body, body_type),
        "toRecipients": create_recipient_list(to_recipients)
    }
    
    if cc_recipients:
        message["ccRecipients"] = create_recipient_list(cc_recipients)
    
    if bcc_recipients:
        message["bccRecipients"] = create_recipient_list(bcc_recipients)
        
    return message