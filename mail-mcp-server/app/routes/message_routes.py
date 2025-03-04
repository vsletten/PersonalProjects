from flask import Blueprint, request, jsonify, session, current_app
from app.services.graph_service import GraphService
from app.auth.oauth import get_token, requires_auth
import logging

message_bp = Blueprint('message', __name__)
logger = logging.getLogger(__name__)

@message_bp.route('/messages', methods=['GET'])
@requires_auth
def list_messages():
    """Get a list of messages from the user's mailbox."""
    try:
        # Get query parameters
        skip = request.args.get('skip', None)
        limit = request.args.get('limit', None)
        filter_query = request.args.get('filter', None)
        select_query = request.args.get('select', None)
        orderby = request.args.get('orderby', None)
        search = request.args.get('search', None)
        
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Get messages
        messages = graph_service.list_messages(
            skip=skip,
            limit=limit,
            filter_query=filter_query,
            select_query=select_query,
            orderby=orderby,
            search=search
        )
        
        return jsonify(messages)
    except Exception as e:
        logger.exception(f"Error listing messages: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>', methods=['GET'])
@requires_auth
def get_message(message_id):
    """Get a specific message by ID."""
    try:
        # Get query parameters
        select_query = request.args.get('select', None)
        
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Get message
        message = graph_service.get_message(
            message_id=message_id,
            select_query=select_query
        )
        
        if not message:
            return jsonify({"error": f"Message with ID {message_id} not found"}), 404
            
        return jsonify(message)
    except Exception as e:
        logger.exception(f"Error getting message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages', methods=['POST'])
@requires_auth
def create_message():
    """Create a new message (draft)."""
    try:
        # Get request body
        message_data = request.json
        if not message_data:
            return jsonify({"error": "No message data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Create message
        created_message = graph_service.create_message(message_data)
        
        return jsonify(created_message), 201
    except Exception as e:
        logger.exception(f"Error creating message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/send', methods=['POST'])
@requires_auth
def send_message(message_id):
    """Send an existing draft message."""
    try:
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Send message
        graph_service.send_message(message_id)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error sending message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>', methods=['PATCH'])
@requires_auth
def update_message(message_id):
    """Update a specific message."""
    try:
        # Get request body
        update_data = request.json
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Update message
        updated_message = graph_service.update_message(message_id, update_data)
        
        return jsonify(updated_message)
    except Exception as e:
        logger.exception(f"Error updating message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>', methods=['DELETE'])
@requires_auth
def delete_message(message_id):
    """Delete a specific message."""
    try:
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Delete message
        graph_service.delete_message(message_id)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error deleting message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/attachments', methods=['GET'])
@requires_auth
def list_attachments(message_id):
    """Get a list of attachments for a specific message."""
    try:
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Get attachments
        attachments = graph_service.list_attachments(message_id)
        
        return jsonify(attachments)
    except Exception as e:
        logger.exception(f"Error listing attachments for message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/attachments', methods=['POST'])
@requires_auth
def add_attachment(message_id):
    """Add an attachment to a specific message."""
    try:
        # Get request body
        attachment_data = request.json
        if not attachment_data:
            return jsonify({"error": "No attachment data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Add attachment
        added_attachment = graph_service.add_attachment(message_id, attachment_data)
        
        return jsonify(added_attachment), 201
    except Exception as e:
        logger.exception(f"Error adding attachment to message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/reply', methods=['POST'])
@requires_auth
def reply_to_message(message_id):
    """Reply to a message."""
    try:
        # Get request body
        reply_data = request.json
        if not reply_data:
            return jsonify({"error": "No reply data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Reply to message
        graph_service.reply_to_message(message_id, reply_data)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error replying to message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/replyAll', methods=['POST'])
@requires_auth
def reply_all_to_message(message_id):
    """Reply all to a message."""
    try:
        # Get request body
        reply_data = request.json
        if not reply_data:
            return jsonify({"error": "No reply data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Reply all to message
        graph_service.reply_all_to_message(message_id, reply_data)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error replying all to message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/messages/<message_id>/forward', methods=['POST'])
@requires_auth
def forward_message(message_id):
    """Forward a message."""
    try:
        # Get request body
        forward_data = request.json
        if not forward_data:
            return jsonify({"error": "No forward data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Forward message
        graph_service.forward_message(message_id, forward_data)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error forwarding message {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@message_bp.route('/sendMail', methods=['POST'])
@requires_auth
def send_mail():
    """Send a new mail in a single operation."""
    try:
        # Get request body
        mail_data = request.json
        if not mail_data:
            return jsonify({"error": "No mail data provided"}), 400
            
        # Create service instance
        token = get_token()
        graph_service = GraphService(token)
        
        # Send mail
        graph_service.send_mail(mail_data)
        
        return "", 204
    except Exception as e:
        logger.exception(f"Error sending mail: {str(e)}")
        return jsonify({"error": str(e)}), 500