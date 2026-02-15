import asyncio
import httpx
import json
import websockets
import random
import string

BASE_URL = "http://localhost/api/v1"
WS_URL = "ws://localhost/api/v1/ws"

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

EMAIL = f"{get_random_string()}@test.com"
PASSWORD = "password123"
DEVICE_ID = f"SH-{get_random_string(5).upper()}"

async def test_websocket_auth():
    async with httpx.AsyncClient() as client:
        # 1. Register User
        print(f"👤 Registering User: {EMAIL}")
        await client.post(f"{BASE_URL}/users/", json={"email": EMAIL, "password": PASSWORD})
        
        # 2. Login
        print("🔑 Logging in...")
        r = await client.post(f"{BASE_URL}/login/access-token", data={"username": EMAIL, "password": PASSWORD})
        if r.status_code != 200:
             print(f"❌ Login Failed: {r.status_code} - {r.text}")
             return
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Register Device
        print(f"📱 Registering Device: {DEVICE_ID}")
        r = await client.post(f"{BASE_URL}/devices/", headers=headers, json={"id": DEVICE_ID, "name": "Secure Device", "type": "esp32"})
        if r.status_code != 200:
             print(f"❌ Device Registration Failed: {r.status_code} - {r.text}")
             return
        api_key = r.json().get("api_key")
        print(f"🔑 API Key Received: {api_key}")
        
        if not api_key:
            print("❌ FAILED: API Key was not returned!")
            return

        # 4. Test Fail: No Auth
        print("🔌 Testing Connection (No Auth) - Should Fail...")
        try:
            async with websockets.connect(f"{WS_URL}/{DEVICE_ID}") as ws:
                await ws.recv() # Should raise exception
                print("❌ FAILED: Connection should have been rejected.")
        except Exception:
            print("✅ PASSED: Rejected as expected.")

        # 5. Test Success: Token Auth (User)
        print("🔌 Testing Connection (User Token) - Should Pass...")
        try:
            async with websockets.connect(f"{WS_URL}/{DEVICE_ID}?token={token}") as ws:
                print("✅ PASSED: User connected.")
        except Exception as e:
            print(f"❌ FAILED: User connection rejected: {e}")

        # 6. Test Success: API Key Query (Device)
        print("🔌 Testing Connection (Device API Key Query) - Should Pass...")
        try:
            async with websockets.connect(f"{WS_URL}/{DEVICE_ID}?api_key={api_key}") as ws:
                print("✅ PASSED: Device connected (Query Param).")
        except Exception as e:
            print(f"❌ FAILED: Device connection rejected: {e}")
            
        # 7. Test Success: API Key Header (Device)
        print("🔌 Testing Connection (Device API Key Header) - Should Pass...")
        try:
            # Note: websockets lib supports extra_headers
            async with websockets.connect(f"{WS_URL}/{DEVICE_ID}", extra_headers={"Authorization": f"Bearer {api_key}"}) as ws:
                print("✅ PASSED: Device connected (Header).")
        except Exception as e:
            print(f"❌ FAILED: Device connection rejected (Header): {e}")

        # 8. Test Convenience Endpoint
        print("💡 Testing Convenience Endpoint (Turn Relay ON)...")
        r = await client.post(f"{BASE_URL}/devices/{DEVICE_ID}/relays/relay1/on", headers=headers)
        if r.status_code == 200 and r.json()["state"]["relay1"]["state"] == True:
             print("✅ PASSED: Relay turned ON.")
        else:
             print(f"❌ FAILED: {r.text}")

if __name__ == "__main__":
    asyncio.run(test_websocket_auth())
