import base64
import json
import logging

logger = logging.getLogger(__name__)

def encode_attachment_content(file_content):
    """
    Encode file content to base64 for attachment.
    
    Args:
        file_content (bytes): File content as bytes
        
    Returns:
        str: Base64 encoded file content
    """
    try:
        encoded = base64.b64encode(file_content).decode('utf-8')
        return encoded
    except Exception as e:
        logger.exception(f"Error encoding attachment content: {str(e)}")
        raise

def decode_attachment_content(base64_content):
    """
    Decode base64 content from attachment.
    
    Args:
        base64_content (str): Base64 encoded content
        
    Returns:
        bytes: Decoded file content
    """
    try:
        decoded = base64.b64decode(base64_content)
        return decoded
    except Exception as e:
        logger.exception(f"Error decoding attachment content: {str(e)}")
        raise

def format_email_address(name, address):
    """
    Format email address for Microsoft Graph API.
    
    Args:
        name (str): Display name
        address (str): Email address
        
    Returns:
        dict: Formatted email address
    """
    return {
        "emailAddress": {
            "name": name,
            "address": address
        }
    }

def create_recipient_list(recipients):
    """
    Create a list of recipients in the correct format.
    
    Args:
        recipients (list): List of dicts with 'name' and 'address' keys
        
    Returns:
        list: List of formatted recipients
    """
    formatted_recipients = []
    
    for recipient in recipients:
        formatted_recipients.append(format_email_address(
            recipient.get('name', ''),
            recipient.get('address', '')
        ))
    
    return formatted_recipients

def create_message_body(content, content_type='html'):
    """
    Create a message body in the correct format.
    
    Args:
        content (str): Message content
        content_type (str): Content type ('html' or 'text')
        
    Returns:
        dict: Formatted message body
    """
    return {
        "contentType": content_type,
        "content": content
    }

def create_file_attachment(name, content_bytes, content_type):
    """
    Create a file attachment in the correct format.
    
    Args:
        name (str): File name
        content_bytes (bytes): File content
        content_type (str): MIME type
        
    Returns:
        dict: Formatted file attachment
    """
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": name,
        "contentType": content_type,
        "contentBytes": encode_attachment_content(content_bytes)
    }

def parse_odata_next_link(next_link):
    """
    Parse OData next link to extract skip token.
    
    Args:
        next_link (str): OData next link
        
    Returns:
        str: Skip token
    """
    if not next_link:
        return None
        
    # Find the skiptoken parameter
    if "$skiptoken=" in next_link:
        parts = next_link.split("$skiptoken=")
        if len(parts) > 1:
            return parts[1].split("&")[0]  # Get the skiptoken value
    
    return None