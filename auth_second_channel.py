import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for YouTube Uploads
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"

def get_new_token():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ ERROR: {CLIENT_SECRET_FILE} not found! Please download it from Google Cloud Console first.")
        return

    print("Starting Authorization for AKONYMOUS...")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save to a specific file for AKONYMOUS
    token_filename = "token_akonymous.json"
    with open(token_filename, "w") as token:
        token.write(creds.to_json())

    print(f"✅ SUCCESS! New token saved as: {token_filename}")
    print("--- COPY THE CONTENT BELOW FOR GITHUB SECRETS ---")
    with open(token_filename, "r") as f:
        print(f.read())
    print("--------------------------------------------------")

if __name__ == "__main__":
    get_new_token()
