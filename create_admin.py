import sys
import os
import secrets
import bcrypt
import pyotp
from app import create_app
from utils.db import execute_db

app = create_app()
with app.app_context():
    username = sys.argv[1] if len(sys.argv) > 1 else os.getenv('ADMIN_USERNAME', 'admin')
    
    admin_env_pass = os.getenv('ADMIN_PASSWORD')
    if len(sys.argv) > 2:
        password = sys.argv[2]
    elif admin_env_pass:
        password = admin_env_pass
    else:
        password = secrets.token_urlsafe(16) + '!1Aa'
        print(f'[SECURITY NOTICE] No password provided. Generated secure admin password: {password}')

    email = sys.argv[3] if len(sys.argv) > 3 else os.getenv('ADMIN_EMAIL', 'admin@anvayavistara.in')
    phone = sys.argv[4] if len(sys.argv) > 4 else None

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    totp_secret = pyotp.random_base32()
    execute_db(
        '''INSERT INTO users (username, password_hash, full_name, role, phone, email, totp_secret, is_active)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
           ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash), email=VALUES(email), phone=VALUES(phone)''',
        (username, hashed, 'Master Admin', 'system_admin', phone, email, totp_secret)
    )
    print(f'Admin created/updated successfully: username={username}, email={email}')
