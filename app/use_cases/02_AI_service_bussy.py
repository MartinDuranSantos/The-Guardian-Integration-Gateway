import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

def send_secure_inquiry(user_id: str, message: str):
    """
    Sends a POST request to the /secure-inquiry endpoint.
    """
    url = "http://localhost:8000/secure-inquiry"

    payload = {
        "userId": user_id,
        "message": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

        data = response.json()
        print("✅ Success!")
        print(json.dumps(data, indent=2))
        return data

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Is it running on localhost:8000?")
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


# ─── Example Usage ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example with PII (email, SSN, credit card)

    for i in range(4):
        result = send_secure_inquiry(
            user_id="usr_42",
            message=(
                f"Hello, my email is {os.getenv('AliceEmail')}, "
                f"my SSN is {os.getenv('AliceSSN')}, "
                f"and my credit card is {os.getenv('AliceCreditCard')}. "
                "Can you help me with my account?"
            )
        )