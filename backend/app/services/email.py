"""
Real email service using aiosmtplib + Gmail SMTP.
Set SMTP_EMAIL and SMTP_PASSWORD in Render environment variables.
SMTP_PASSWORD must be a Gmail App Password (not your normal Gmail password).
"""
import asyncio
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings


async def _send_async(to_email: str, subject: str, html_body: str):
    """Send an email via Gmail SMTP."""
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        print(f"[Email] SMTP not configured — skipping email to {to_email}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"HomeControl <{settings.SMTP_EMAIL}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.SMTP_EMAIL,
            password=settings.SMTP_PASSWORD,
        )
        print(f"[Email] ✅ Email sent to {to_email}")
    except Exception as e:
        print(f"[Email] ❌ Failed to send email to {to_email}: {e}")


def _welcome_html(email: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0f; color: #f1f5f9; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 520px; margin: 40px auto; background: #111118; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); }}
    .header {{ background: linear-gradient(135deg, #7c3aed, #06b6d4); padding: 36px 32px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 1.8em; color: white; }}
    .header p  {{ margin: 6px 0 0; color: rgba(255,255,255,0.8); }}
    .body {{ padding: 32px; }}
    .body p {{ color: #94a3b8; line-height: 1.7; margin: 0 0 16px; }}
    .btn {{ display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #7c3aed, #06b6d4); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 8px 0; }}
    .footer {{ text-align: center; padding: 20px; color: #475569; font-size: 0.8em; border-top: 1px solid rgba(255,255,255,0.06); }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🏠 HomeControl</h1>
      <p>Smart Home Platform</p>
    </div>
    <div class="body">
      <p>Hi <strong>{email}</strong>,</p>
      <p>Welcome to <strong>HomeControl</strong>! Your account has been successfully created.</p>
      <p>You can now log in and start controlling your smart home devices from anywhere in the world.</p>
      <p style="text-align:center; margin: 28px 0;">
        <a class="btn" href="https://homecontrol-cloud.onrender.com/index.html">Go to Dashboard →</a>
      </p>
      <p>If you did not create this account, you can safely ignore this email.</p>
    </div>
    <div class="footer">
      © 2025 HomeControl · Built with ❤️
    </div>
  </div>
</body>
</html>
"""


async def send_welcome_email(email: str):
    """Send welcome/confirmation email after user registration."""
    html = _welcome_html(email)
    await _send_async(email, "Welcome to HomeControl! 🏠", html)


def send_welcome_email_background(email: str):
    """Fire-and-forget wrapper for use in FastAPI background tasks."""
    asyncio.create_task(_send_async(email, "Welcome to HomeControl! 🏠", _welcome_html(email)))


async def send_admin_promotion_email(email: str):
    """Send an email notifying a user they have been promoted to admin/superuser."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0f; color: #f1f5f9; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 520px; margin: 40px auto; background: #111118; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); }}
    .header {{ background: linear-gradient(135deg, #7c3aed, #f59e0b); padding: 36px 32px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 1.8em; color: white; }}
    .header p  {{ margin: 6px 0 0; color: rgba(255,255,255,0.8); }}
    .body {{ padding: 32px; }}
    .body p {{ color: #94a3b8; line-height: 1.7; margin: 0 0 16px; }}
    .badge {{ display:inline-block; padding:6px 16px; background:linear-gradient(135deg,#7c3aed,#f59e0b); border-radius:20px; color:white; font-weight:700; font-size:0.9em; }}
    .btn {{ display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #7c3aed, #06b6d4); color: white; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 8px 0; }}
    .footer {{ text-align: center; padding: 20px; color: #475569; font-size: 0.8em; border-top: 1px solid rgba(255,255,255,0.06); }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🛡️ Admin Access Granted</h1>
      <p>HomeControl Platform</p>
    </div>
    <div class="body">
      <p>Hi <strong>{email}</strong>,</p>
      <p>Great news! Your account has been upgraded. You are now a <span class="badge">⭐ SUPER ADMIN</span> on HomeControl.</p>
      <p>You now have full access to the Admin Panel where you can manage all devices, users, and firmware.</p>
      <p style="text-align:center; margin: 28px 0;">
        <a class="btn" href="https://homecontrol-cloud.onrender.com/admin.html">Open Admin Panel →</a>
      </p>
      <p>If you did not expect this, please contact your system administrator immediately.</p>
    </div>
    <div class="footer">
      © 2025 HomeControl · Built with ❤️
    </div>
  </div>
</body>
</html>
"""
    await _send_async(email, "You've been promoted to Admin! 🛡️", html)

