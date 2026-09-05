from app import create_app
from utils.db import execute_db
import bcrypt
import pyotp

app = create_app()
with app.app_context():
    username = 'admin'
    password = 'adminpassword'
    email = 'admin@example.com'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    totp_secret = pyotp.random_base32()
    execute_db('INSERT INTO users (username, password_hash, full_name, role, phone, email, totp_secret, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, 1) ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash), email=VALUES(email)', (username, hashed, 'Master Admin', 'system_admin', '1234567890', email, totp_secret))
    print('Admin created/updated: username=' + username + ', password=' + password + ', email=' + email)
