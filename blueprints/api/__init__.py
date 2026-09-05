

from flask import Blueprint, request, jsonify
from utils.auth_helpers import get_current_user
from utils.db import query_db

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health')
def health_check():
    return {'status': 'ok'}

@api_bp.route('/notifications')
def get_notifications():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    unread = request.args.get('unread')
    if unread == '1':
        result = query_db('SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = 0', (user['id'],), one=True)
        return jsonify({'count': result['count'] if result else 0})
    
    notifs = query_db('SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 50', (user['id'],))
    return jsonify({'notifications': notifs})
