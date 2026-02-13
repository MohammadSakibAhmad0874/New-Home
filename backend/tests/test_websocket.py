import asyncio
import httpx
import json
import websockets
import random
import string

BASE_URL = "http://localhost/api/v1"
WS_URL = "ws://localhost/api/v1/ws"
print(f"Testing against {BASE_URL}")

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

EMAIL = f"{get_random_string()}@test.com"
PASSWORD = "password123"
DEVICE_ID = f"SH-{get_random_string(5).upper()}"

async def test_websocket():
    async with httpx.AsyncClient() as client:
        # 1. Register User
        print(f"👤 Registering User: {EMAIL}")
        r = await client.post(f"{BASE_URL}/users/", json={"email": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
             print(f"❌ User Registration Failed: {r.text}")
             # If user exists, try login anyway
        
        # 2. Login
        print("🔑 Logging in...")
        r = await client.post(f"{BASE_URL}/login/access-token", data={"username": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
            print(f"❌ Login Failed: {r.text}")
            return
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Register Device
        print(f"📱 Registering Device: {DEVICE_ID}")
        r = await client.post(f"{BASE_URL}/devices/", headers=headers, json={"id": DEVICE_ID, "name": "Test Device", "type": "esp32"})
        if r.status_code != 200:
            print(f"❌ Device Registration Failed: {r.text}")
            return

        # 4. Start WebSocket Connection
        uri = f"{WS_URL}/{DEVICE_ID}"
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # 5. Simulate Device State Update via REST (in background)
            print("📡 Sending update via REST...")
            # Note: update_device_state endpoint doesn't require auth in code currently, but we pass headers just in case
            response = await client.put(
                f"{BASE_URL}/devices/{DEVICE_ID}/state",
                json={"relay1": {"state": True}, "relay3": {"state": False}},
                headers=headers
            )
            print(f"REST Update Response: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ REST Update Failed: {response.text}")

            # 6. Wait for WebSocket Message
            print("⏳ Waiting for broadcast...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📩 Received: {data}")
                
                if data["type"] == "update" and data["data"]["relay1"]["state"] == True:
                    print("✅ TEST PASSED: Realtime update received!")
                else:
                    print("❌ TEST FAILED: Verification failed.")
                    
            except asyncio.TimeoutError:
                print("❌ TEST FAILED: Timeout waiting for message.")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except Exception as e:
        print(f"Error: {e}")
