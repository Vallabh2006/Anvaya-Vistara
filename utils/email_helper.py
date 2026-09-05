import os
import re
import smtplib
from email.message import EmailMessage
from flask import current_app

SMTP_HOST = "smtppro.zoho.in"
SMTP_PORT = 465

EMAIL = os.getenv("ZOHO_EMAIL")
PASSWORD = os.getenv("ZOHO_PASSWORD")


def send_email(to: str, subject: str, body: str, html_body: str = None) -> bool:
    try:
        if current_app and current_app.config.get('TESTING'):
            print(f"[TESTING] Suppressed outgoing email to {to}: {subject}")
            return True
    except Exception:
        pass

    if not EMAIL or not PASSWORD:
        print("Email credentials not configured in environment. Logged message:")
        print("To:", to)
        print("Subject:", subject)
        print("Body:", body)
        return False
        
    if not to or not subject or not body:
        print("Recipient email, subject, and body are required.")
        return False

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, to.strip()):
        print("Invalid recipient email address:", to)
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to.strip()
        msg.set_content(body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_otp_email(to_email: str, full_name: str, otp_code: str) -> bool:
    subject = "Anvaya Vistara - Your Account Verification OTP"
    
    text_body = f"""Hello {full_name or 'Patient'},

Your verification passcode is: {otp_code}

This code is valid for 10 minutes. Do not share this code with anyone.

Best regards,
Anvaya Vistara Health Network
"""

    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>Anvaya Vistara Account Verification</h2>
        <p>Hello <strong>{full_name or 'Patient'}</strong>,</p>
        <p>Use the following 6-digit verification code to complete your verification:</p>
        <div style="background: #f0f4f8; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #1e3a8a;">
            {otp_code}
        </div>
        <p>This code will expire in 10 minutes.</p>
    </div>
    """

    return send_email(to_email, subject, text_body, html_body)


def mask_email(email_str: str) -> str:
    if not email_str or '@' not in email_str:
        return email_str or ''
    parts = email_str.split('@', 1)
    user_part = parts[0]
    domain_part = parts[1]

    if len(user_part) <= 2:
        masked_user = user_part[0] + '***'
    elif len(user_part) <= 5:
        masked_user = user_part[0] + ('*' * (len(user_part) - 2)) + user_part[-1]
    else:
        masked_user = user_part[:2] + ('*' * (len(user_part) - 3)) + user_part[-1]

    domain_subparts = domain_part.split('.', 1)
    if len(domain_subparts) == 2:
        dom_name = domain_subparts[0]
        dom_ext = domain_subparts[1]
        if len(dom_name) <= 2:
            masked_dom = dom_name[0] + '***'
        elif len(dom_name) == 3:
            masked_dom = dom_name[0] + '*' + dom_name[-1]
        else:
            masked_dom = dom_name[0] + ('*' * (len(dom_name) - 2)) + dom_name[-1]
        return f"{masked_user}@{masked_dom}.{dom_ext}"
    else:
        return f"{masked_user}@{domain_part}"


def send_password_reset_email(to_email: str, full_name: str, otp_code: str) -> bool:
    subject = "Anvaya Vistara - Password Reset Code"

    text_body = f"""Hello {full_name or 'User'},

You requested a password reset for your Anvaya Vistara account.
Your 6-digit verification code is: {otp_code}

This code expires in 10 minutes. If you did not request this, please ignore this email.

Best regards,
Anvaya Vistara Security Team
"""

    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>Password Reset Request</h2>
        <p>Hello <strong>{full_name or 'User'}</strong>,</p>
        <p>Your password reset verification code is:</p>
        <div style="background: #eef2ff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #1e40af;">
            {otp_code}
        </div>
        <p>This code is valid for 10 minutes.</p>
    </div>
    """

    return send_email(to_email, subject, text_body, html_body)


def send_email_change_otp(to_new_email: str, full_name: str, otp_code: str) -> bool:
    subject = "Anvaya Vistara - Confirm Email Address Change"

    text_body = f"""Hello {full_name or 'User'},

Your 6-digit verification code to confirm your email address change is: {otp_code}

This code expires in 10 minutes.

Best regards,
Anvaya Vistara Security Team
"""

    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>Confirm Email Change</h2>
        <p>Hello <strong>{full_name or 'User'}</strong>,</p>
        <p>Your verification code to update your registered email address is:</p>
        <div style="background: #eef2ff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #1e40af;">
            {otp_code}
        </div>
        <p>This code is valid for 10 minutes.</p>
    </div>
    """

    return send_email(to_new_email, subject, text_body, html_body)


def send_staff_invite_email(to_email: str, full_name: str, invite_link: str, role: str) -> bool:
    subject = "Anvaya Vistara - Staff Account Invitation"

    text_body = f"""Hello {full_name or 'Staff Member'},

You have been invited to join the Anvaya Vistara Healthcare Network as a {role}.
Please use the following link to activate your account:
{invite_link}

Best regards,
Anvaya Vistara Administration
"""

    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>Staff Account Invitation</h2>
        <p>Hello <strong>{full_name or 'Staff Member'}</strong>,</p>
        <p>You have been invited to join the Anvaya Vistara Healthcare Network as a <strong>{role}</strong>.</p>
        <p><a href="{invite_link}" style="display: inline-block; background: #1e40af; color: #fff; padding: 10px 18px; text-decoration: none; border-radius: 6px;">Activate Account</a></p>
    </div>
    """

    return send_email(to_email, subject, text_body, html_body)
