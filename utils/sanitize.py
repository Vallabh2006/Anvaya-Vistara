import re
from markupsafe import escape

def sanitize_text(text, max_length=5000):
    if not text:
        return ''
    text = str(text).strip()
    if len(text) > max_length:
        text = text[:max_length]
    return str(escape(text))

def sanitize_csv_cell(cell):
    if cell is None:
        return ''
    cell_str = str(cell).strip()
    if cell_str and cell_str[0] in ('=', '+', '-', '@', '\t', '\r'):
        cell_str = "'" + cell_str
    return cell_str

def validate_identifier(value, pattern=r'^[a-zA-Z0-9._@-]+$', max_len=100):
    if not value:
        return None
    val_str = str(value).strip()
    if len(val_str) > max_len or not re.match(pattern, val_str):
        return None
    return val_str

def validate_email(email):
    if not email:
        return False
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(email_pattern, str(email).strip()))

def validate_phone(phone):
    if not phone:
        return True
    phone_pattern = r"^[0-9+\-\s()]{7,20}$"
    return bool(re.match(phone_pattern, str(phone).strip()))

def validate_username(username):
    if not username:
        return False
    username_pattern = r"^[a-z0-9._]{3,30}$"
    return bool(re.match(username_pattern, str(username).strip()))

def validate_patient_id(pid):
    if not pid:
        return False
    patient_id_pattern = r"^PAT-\d{4}-\d{4,}$"
    return bool(re.match(patient_id_pattern, str(pid).strip()))

def validate_center_id(cid):
    if not cid:
        return False
    center_id_pattern = r"^FAC-[A-Z0-9]+-\d{2}$"
    return bool(re.match(center_id_pattern, str(cid).strip()))
