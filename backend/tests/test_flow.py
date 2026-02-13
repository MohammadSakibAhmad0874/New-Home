import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test@example.com"
PASSWORD = "password123"
DEVICE_ID = "SH-001"

async def main():
    async with httpx.AsyncClient() as client:
        print("1. Registering User...")
        response = await client.post(f"{BASE_URL}/users/", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        if response.status_code == 200:
            print("   User registered successfully.")
        elif response.status_code == 400 and "exists" in response.text:
            print("   User already exists.")
        else:
            print(f"   Failed: {response.text}")
            return

        print("\n2. Logging in...")
        response = await client.post(f"{BASE_URL}/login/access-token", data={
            "username": EMAIL,
            "password": PASSWORD
        })
        if response.status_code != 200:
            print(f"   Login failed: {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   Login successful. Token received.")

        print("\n3. Registering Device...")
        response = await client.post(f"{BASE_URL}/devices/", headers=headers, json={
            "id": DEVICE_ID,
            "name": "Living Room Switch",
            "type": "esp32-4ch"
        })
        if response.status_code == 200:
            print("   Device registered.")
        elif response.status_code == 400 and "exists" in response.text:
            print("   Device already exists.")
        else:
            print(f"   Failed: {response.text}")

        print("\n4. Simulating ESP32 Heartbeat...")
        response = await client.post(f"{BASE_URL}/devices/{DEVICE_ID}/heartbeat", headers=headers, json={
            "ip": "192.168.1.100"
        })
        print(f"   Heartbeat status: {response.status_code}")

        print("\n5. Updating Device State (from ESP32)...")
        new_state = {"relay1": {"state": True}, "relay2": {"state": False}}
        response = await client.put(f"{BASE_URL}/devices/{DEVICE_ID}/state", headers=headers, json=new_state)
        print(f"   Update status: {response.status_code}")
        print(f"   Response: {response.json()}")

        print("\n6. Fetching Device State (Frontend)...")
        response = await client.get(f"{BASE_URL}/devices/{DEVICE_ID}", headers=headers)
        device = response.json()
        print(f"   Device State: {device.get('start_state')}")
        print(f"   Online: {device.get('online')}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the backend is running on http://localhost:8000")
