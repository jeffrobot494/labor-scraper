import requests
import os

def create_session():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    homepage_url = "https://www.efast.dol.gov/5500Search/"
    response = session.get(homepage_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to load homepage. Status code: {response.status_code}")
        return None

    print("✅ Successfully loaded homepage and captured session cookies.")
    return session

def download_filing_pdf(session, ack_id, pdf_path, save_folder="./downloads"):
    base_url = "https://www.efast.dol.gov"
    full_url = base_url + pdf_path

    headers = {
        "Referer": "https://www.efast.dol.gov/5500Search/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    response = session.get(full_url, headers=headers, stream=True)

    if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, f"{ack_id}.pdf")
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Downloaded PDF: {save_path}")
    else:
        print(f"❌ Failed to download valid PDF for {ack_id}.")
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Response content (truncated): {response.text[:300]}")  # for debug

if __name__ == "__main__":
    ack_id = "20240924160451NAL0013030593001"
    pdf_path = "/2024/09/24/20240924160451NAL0013030593001.pdf"

    session = create_session()
    if session:
        download_filing_pdf(session, ack_id, pdf_path)
