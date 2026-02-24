"""Just prints the correct password hash - no DB connection needed."""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from core.security import get_password_hash

password = "MrNoor@874"
hashed = get_password_hash(password)
print("\n✅ Copy this hash and paste it into pgAdmin SQL:\n")
print(f"UPDATE users SET hashed_password = '{hashed}', is_superuser = true WHERE email = 'ahmadsakib263@gmail.com';\n")
