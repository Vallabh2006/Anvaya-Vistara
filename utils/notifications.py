"""
Notification helper utilities for creating and dispatching notifications.
"""
from datetime import datetime
from utils.db import query_db, execute_db


def create_notification(user_id, title, body, link=None):
    """
    Inserts a notification record into the notifications table.
    """
    if not user_id or not title:
        return None
    try:
        notif_id = execute_db(
            """
            INSERT INTO notifications (user_id, title, body, link, is_read, created_at)
            VALUES (%s, %s, %s, %s, 0, NOW())
            """,
            (user_id, title, body, link)
        )
        return notif_id
    except Exception as e:
        print(f"[create_notification error]: {e}")
        return None


def notify_patient(patient_id, title, body, link=None):
    """
    Looks up the linked user ID for a given patient_id (or patient object)
    and creates a notification if the linked user exists.
    """
    if not patient_id or not title:
        return None

    try:
        pat_id = patient_id["id"] if isinstance(patient_id, dict) else str(patient_id)
        patient = query_db("SELECT linked_user_id FROM patients WHERE id = %s", (pat_id,), one=True)
        if patient and patient.get("linked_user_id"):
            return create_notification(patient["linked_user_id"], title, body, link)
    except Exception as e:
        print(f"[notify_patient error]: {e}")
        return None

    return None
