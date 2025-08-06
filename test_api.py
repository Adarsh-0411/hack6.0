import requests
import json

def test_query_system():
    endpoint = "http://localhost:8000/api/v1"

    input_payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer c81068530ecf2d60265383fb699327a488c89efcf3ba6b1e0e434f2b673d95c9"
    }

    try:
        print("📡 Initiating API call to local server...")
        print(f"Questions Count: {len(input_payload['questions'])}")
        response = requests.post(endpoint, json=input_payload, headers=headers)

        if response.status_code == 200:
            print("✅ Response received successfully!")
            data = response.json()
            print("\n📌 Extracted Answers:")
            for idx, item in enumerate(data['answers'], 1):
                print(f"{idx}. {item['question']}\n   Answer: {item['answer']}")
                print(f"   Confidence: {item['rationale'].get('confidence_factors', 'N/A')}")
                print(f"   Evidence Count: {len(item['rationale'].get('key_evidence', []))}")
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("🚫 Could not connect. Make sure server is running at localhost:8000")
    except Exception as err:
        print(f"⚠️ Error occurred: {err}")

if __name__ == "__main__":
    test_query_system()
