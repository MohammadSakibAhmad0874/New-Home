import time

def send_welcome_email(email: str):
    """
    Simulate sending an email with template rendering.
    """
    print(f"[Notification Service] Preparing email for {email}...")
    
    # Simulate template rendering
    template = f"""
    <html>
        <body>
            <h1>Welcome to HomeControl!</h1>
            <p>Hello {email},</p>
            <p>Your account is now active.</p>
        </body>
    </html>
    """
    
    # Simulate network delay (IO bound)
    time.sleep(1.5)
    
    # In a real scenario, use aiosmtplib here
    print(f"[Notification Service] POST /sendmail 200 OK")
    print(f"[Notification Service] Email sent successfully to {email}.")
    return {"sent": True, "recipient": email}
