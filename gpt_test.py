import requests
import json
import time

def create_session():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    # Step 1: Load homepage to get session cookies
    homepage_url = "https://www.efast.dol.gov/5500Search/"
    response = session.get(homepage_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to load homepage. Status code: {response.status_code}")
        return None

    print("✅ Successfully loaded homepage and captured session cookies.")
    return session

def search_filing(session, ack_id):
    base_url = "https://www.efast.dol.gov/services/afs"

    params = {
        "q.parser": "lucene",
        "size": 200,
        "sort": "planname asc",
        "q": f'(((ackid:"{ack_id}" AND -(dcgind:"1"))))',
        "facet.planyear": "{size:30}",
        "facet.plancode": "{size:100}",
        "facet.assetseoy": "{buckets:[\"{,100000]\",\"[100001,500000]\",\"[500001,1000000]\",\"[1000001,10000000]\",\"[10000001,}\"]}",
        "facet.plantype": "{size:20}",
        "facet.businesscodecat": "{size:30}",
        "facet.businesscode": "{size:30}",
        "facet.state": "{size:100}",
        "facet.countrycode": "{buckets:[\"CA\",\"GB\",\"BM\",\"KY\"]}",
        "facet.formyear": "{size:30}"
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.efast.dol.gov/5500Search/"
    }

    response = session.get(base_url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"❌ Search failed. Status code: {response.status_code}")
        return None

    return response.json()

def main():
    ack_id = "20240924160451NAL0013030593001"  # Example Filing ID

    session = create_session()
    if not session:
        return

    time.sleep(2)  # Small polite delay

    result = search_filing(session, ack_id)
    if not result:
        return

    hits = result.get("hits", {}).get("hit", [])

    if not hits:
        print(f"No filings found for ACK_ID: {ack_id}")
        return

    print(f"\n✅ Filing(s) found for ACK_ID: {ack_id}")
    
    for idx, hit in enumerate(hits, 1):
        fields = hit.get("fields", {})
        print(f"\nResult #{idx}:")
        print(f"- Plan Name: {fields.get('planname')}")
        print(f"- Sponsor Name: {fields.get('sponsname')}")
        print(f"- Plan Year: {fields.get('planyear')}")
        print(f"- Form Type: {fields.get('formtype')}")
        print(f"- Plan Type: {fields.get('plantype')}")
        print(f"- Filing ID (ACK_ID): {fields.get('ackid')}")

if __name__ == "__main__":
    main()
