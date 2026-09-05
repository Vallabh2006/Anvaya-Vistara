

from functools import wraps
from flask import session, redirect, url_for, abort, request, jsonify, g
from utils.db import query_db


def get_current_user():
    if 'current_user' in g:
        return g.current_user
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = query_db('SELECT * FROM users WHERE id = %s AND is_active = 1', (user_id,), one=True)
    g.current_user = user
    return user


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            if request.path.startswith('/admin'):
                return redirect(url_for('auth.admin_login', next=request.url))
            if request.path.startswith('/dashboard/phc') or request.path.startswith('/phc'):
                return redirect(url_for('auth.phc_login', next=request.url))
            return redirect(url_for('auth.login', next=request.url))
        user = get_current_user()
        if not user:
            session.clear()
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


from flask import flash

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            user = get_current_user()
            if user['role'] not in roles:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                session.clear()
                flash('Access Denied: Please log in with an account that has the correct permissions.', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def facility_scoped(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user.get('facility_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'No facility assigned'}), 403
            abort(403)
        g.facility_id = user['facility_id']
        return f(*args, **kwargs)
    return decorated
