import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Current auth configuration
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"
REDIRECT_URI = "http://localhost"

# The NEW code provided by the user
CODE = "4/0Aci98E8sYxIsH0e9eYOmSUPqKc4phxIJioxBP5bUCuuYRrfzy3X7soC3uYGYENXz7kGcoA"

def exchange_code():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print("❌ ERROR: client_secret.json not found!")
        return

    print("Exchanging NEW code for token...")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES, redirect_uri=REDIRECT_URI)
    
    try:
        flow.fetch_token(code=CODE)
        creds = flow.credentials

        # Save to token_akonymous.json
        token_data = creds.to_json()
        with open("token_akonymous.json", "w") as token_file:
            token_file.write(token_data)

        print("✅ SUCCESS! token_akonymous.json created.")
        print("\n--- NEW TOKEN JSON CONTENT (COPY FOR GITHUB) ---")
        print(token_data)
        print("--------------------------------------------")
    except Exception as e:
        print(f"❌ ERROR: Exchange failed ({e})")

if __name__ == "__main__":
    exchange_code()
