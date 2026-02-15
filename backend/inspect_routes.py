import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
sys.path.append(os.path.dirname(__file__))

# Mock environment variables if needed
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_DB", "homecontrol")

from app.main import app

def list_routes():
    print("🛣️ Routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f" - {route.path} [{route.name}]")
        elif hasattr(route, "path_format"):
            print(f" - {route.path_format} [{route.name}]")

if __name__ == "__main__":
    list_routes()
