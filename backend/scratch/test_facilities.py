import os
import sys

# Ensure backend directory is in the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    print("=== TESTING /facilities/nearby ===")
    # Close to Yelahanka, Bengaluru Urban: lat=13.1, lon=77.6
    response = client.get("/facilities/nearby", params={"lat": 13.1, "lon": 77.6, "limit": 2})
    print(f"Status Code: {response.status_code}")
    print("Response:")
    import json
    print(json.dumps(response.json(), indent=2))
    
    print("\n=== TESTING /facilities/by-pincode ===")
    # Testing for Sulur pincode '641402'
    response = client.get("/facilities/by-pincode", params={"pincode": "641402", "limit": 2})
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_endpoints()
