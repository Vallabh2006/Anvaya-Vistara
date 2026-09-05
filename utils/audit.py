from flask import session, request
from utils.db import execute_db, query_db
import json


def log_audit(action, entity_type=None, entity_id=None, detail=None):
    user_id = session.get('user_id')
    ip = request.remote_addr if request else None
    detail_json = json.dumps(detail) if detail else None

    if user_id:
        try:
            user_exists = query_db('SELECT id FROM users WHERE id = %s', (user_id,), one=True)
            if not user_exists:
                user_id = None
        except Exception:
            user_id = None

    try:
        execute_db(
            'INSERT INTO audit_logs (user_id, action, entity_type, entity_id, detail, ip_address) VALUES (%s, %s, %s, %s, %s, %s)',
            (user_id, action, entity_type, str(entity_id) if entity_id else None, detail_json, ip)
        )
    except Exception:
        pass
