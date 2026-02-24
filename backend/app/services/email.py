"""
Email service using Resend.com API — free, no 2FA needed.
Sign up at https://resend.com and set RESEND_API_KEY in Render environment variables.
Free tier: 100 emails/day.
"""
import httpx
from core.config import settings


async def _send_via_resend(to_email: str, subject: str, html_body: str):
    """Send email via Resend.com REST API."""
    if not settings.RESEND_API_KEY:
        print(f"[Email] RESEND_API_KEY not set — skipping email to {to_email}")
        return

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "HomeControl <onboarding@resend.dev>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                },
                timeout=10,
            )
            if res.status_code in (200, 201):
                print(f"[Email] ✅ Email sent to {to_email}")
            else:
                print(f"[Email] ❌ Resend error {res.status_code}: {res.text}")
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


def _admin_html(email: str) -> str:
    return f"""
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


async def send_welcome_email(email: str):
    """Send welcome/confirmation email after user registration."""
    await _send_via_resend(email, "Welcome to HomeControl! 🏠", _welcome_html(email))


async def send_admin_promotion_email(email: str):
    """Send email notifying a user they have been promoted to admin/superuser."""
    await _send_via_resend(email, "You've been promoted to Admin! 🛡️", _admin_html(email))


def _forgot_password_html(email: str, reset_token: str) -> str:
    reset_url = f"https://homecontrol-cloud.onrender.com/index.html?reset_token={reset_token}"
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0f; color: #f1f5f9; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 520px; margin: 40px auto; background: #111118; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); }}
    .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 36px 32px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 1.8em; color: white; }}
    .header p  {{ margin: 6px 0 0; color: rgba(255,255,255,0.8); }}
    .body {{ padding: 32px; }}
    .body p {{ color: #94a3b8; line-height: 1.7; margin: 0 0 16px; }}
    .btn {{ display: inline-block; padding: 13px 32px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 10px; text-decoration: none; font-weight: 700; margin: 8px 0; font-size: 1em; }}
    .token-box {{ background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2); border-radius: 10px; padding: 14px 18px; font-family: monospace; font-size: 1.05em; color: #a5b4fc; letter-spacing: 0.08em; word-break: break-all; margin: 16px 0; }}
    .warning {{ color: #f87171; font-size: 0.85em; }}
    .footer {{ text-align: center; padding: 20px; color: #475569; font-size: 0.8em; border-top: 1px solid rgba(255,255,255,0.06); }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🔑 Password Reset</h1>
      <p>HomeControl Cloud</p>
    </div>
    <div class="body">
      <p>Hi <strong>{email}</strong>,</p>
      <p>We received a request to reset your HomeControl password. Click the button below to set a new password.</p>
      <p style="text-align:center; margin: 28px 0;">
        <a class="btn" href="{reset_url}">Reset My Password →</a>
      </p>
      <p>Or copy this reset token and use it on the login page:</p>
      <div class="token-box">{reset_token}</div>
      <p class="warning">⚠️ This link expires in <strong>30 minutes</strong>. If you did not request a password reset, please ignore this email — your account is safe.</p>
    </div>
    <div class="footer">
      © 2025 HomeControl · Built with ❤️
    </div>
  </div>
</body>
</html>
"""


async def send_forgot_password_email(email: str, reset_token: str):
    """Send password reset email with a one-time token."""
    await _send_via_resend(
        email,
        "Reset Your HomeControl Password 🔑",
        _forgot_password_html(email, reset_token)
    )
