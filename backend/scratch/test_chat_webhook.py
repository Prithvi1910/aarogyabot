import os
import sys
import json

# Ensure backend directory is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_endpoints():
    print("=== TESTING /chat ENDPOINT ===")
    
    # 1. Pincode lookup test (Sulur 641402)
    print("\n1. Pincode Lookup (Valid PIN: 641402)")
    response = client.post("/chat/", json={"message": "641402", "session_id": "test_sess_1"})
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # 2. Pincode lookup test (No facilities found: 999999)
    print("\n2. Pincode Lookup (Invalid/Empty PIN: 999999)")
    response = client.post("/chat/", json={"message": "999999", "session_id": "test_sess_2"})
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

    # 3. Message in English (Urgency VISIT_PHC due to fever)
    print("\n3. English message (Fever symptom - VISIT_PHC)")
    response = client.post("/chat/", json={"message": "I have had a high fever for two days.", "session_id": "test_sess_3"})
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

    # 4. Message in Hindi (Urgency EMERGENCY due to chest pain)
    print("\n4. Hindi message (Chest pain symptom - EMERGENCY)")
    # 'mujhe bukhar aur chest pain hai' -> Hinglish/Hindi
    response = client.post("/chat/", json={"message": "mujhe severe chest pain hai aur bahut ghabrahat ho rahi hai", "session_id": "test_sess_4"})
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_webhook_endpoints():
    print("\n=== TESTING /webhook/whatsapp ENDPOINTS ===")
    
    # 1. GET request for Twilio verification
    print("\n1. GET Verification")
    response = client.get("/webhook/whatsapp")
    print(f"Status Code: {response.status_code}")
    print(f"Response content: {response.text}")

    # 2. POST with form data: Pincode
    print("\n2. POST Pincode (641402)")
    response = client.post(
        "/webhook/whatsapp",
        data={"Body": "641402", "From": "whatsapp:+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # 3. POST with form data: English message (SELF_CARE)
    print("\n3. POST English (Self-care, mild tired)")
    response = client.post(
        "/webhook/whatsapp",
        data={"Body": "Just feeling a bit tired, no other symptoms.", "From": "whatsapp:+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # 4. POST with form data: Hindi message (EMERGENCY)
    print("\n4. POST Hindi (Chest pain - EMERGENCY)")
    response = client.post(
        "/webhook/whatsapp",
        data={"Body": "mujhe chest pain aur heart attack jaisa lag raha hai", "From": "whatsapp:+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    print("\n=== TESTING /webhook/sms ENDPOINTS ===")
    
    # 5. GET request for SMS verification
    print("\n5. GET SMS Verification")
    response = client.get("/webhook/sms")
    print(f"Status Code: {response.status_code}")
    print(f"Response content: {response.text}")

    # 6. POST SMS: Pincode
    print("\n6. POST SMS Pincode (641402)")
    response = client.post(
        "/webhook/sms",
        data={"Body": "641402", "From": "+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # 7. POST SMS: English message (SELF_CARE)
    print("\n7. POST SMS English (Self-care, mild tired)")
    response = client.post(
        "/webhook/sms",
        data={"Body": "Just feeling a bit tired, no other symptoms.", "From": "+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # 8. POST WhatsApp with From as non-whatsapp to test auto-SMS detection
    print("\n8. POST WhatsApp endpoint but using SMS phone number")
    response = client.post(
        "/webhook/whatsapp",
        data={"Body": "Just feeling a bit tired, no other symptoms.", "From": "+14155238886"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    test_chat_endpoints()
    test_webhook_endpoints()
