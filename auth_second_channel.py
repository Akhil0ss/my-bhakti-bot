import argparse
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
import urllib.parse
import urllib.request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILENAME = "token_akonymous.json"


def load_client_config():
    if not os.path.exists(CLIENT_SECRET_FILE):
        raise FileNotFoundError(
            f"{CLIENT_SECRET_FILE} not found. Put your Google OAuth client JSON in the project root first."
        )

    with open(CLIENT_SECRET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = data.get("installed") or data.get("web")
    if not config:
        raise ValueError("client_secret.json must contain an 'installed' or 'web' OAuth client.")

    redirect_uris = config.get("redirect_uris") or ["http://localhost"]
    return {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "auth_uri": config["auth_uri"],
        "token_uri": config["token_uri"],
        "redirect_uri": redirect_uris[0],
    }


def build_auth_url(config):
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    url = f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"
    return url, state


def parse_code(callback_value):
    value = callback_value.strip()
    if not value:
        raise ValueError("No callback URL or code was provided.")

    if "code=" in value:
        parsed = urllib.parse.urlparse(value)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [None])[0]
        if code:
            return code

    return value


def exchange_code_for_token(config, code):
    payload = urllib.parse.urlencode(
        {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        config["token_uri"],
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        token_data = json.loads(response.read().decode("utf-8"))

    expires_in = int(token_data.get("expires_in", 3600))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    return {
        "token": token_data.get("access_token", ""),
        "refresh_token": token_data.get("refresh_token", ""),
        "token_uri": config["token_uri"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "scopes": SCOPES,
        "account": "",
        "universe_domain": "googleapis.com",
        "expiry": expiry.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def get_new_token(callback_value=None):
    config = load_client_config()
    auth_url, _ = build_auth_url(config)

    print("Starting Authorization for AKONYMOUS...")
    print("\nOpen this URL in your browser and complete the login:")
    print(auth_url)

    if callback_value:
        raw_callback = callback_value
    else:
        raw_callback = input(
            "\nAfter login, paste the full redirected URL or the authorization code here: "
        )

    code = parse_code(raw_callback)
    token_data = exchange_code_for_token(config, code)

    with open(TOKEN_FILENAME, "w", encoding="utf-8") as token:
        token.write(json.dumps(token_data))

    print(f"\nSUCCESS! New token saved as: {TOKEN_FILENAME}")
    print("--- COPY THE CONTENT BELOW FOR GITHUB SECRETS ---")
    print(json.dumps(token_data))
    print("--------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Authorize the AKONYMOUS YouTube channel")
    parser.add_argument(
        "--callback-url",
        type=str,
        help="Paste the full redirected URL or code directly to finish the token exchange.",
    )
    args = parser.parse_args()
    get_new_token(callback_value=args.callback_url)
