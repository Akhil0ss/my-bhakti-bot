import os
import random
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "client_secret.json"


def _load_credentials(token_file, token_secret_env=None):
    """Load OAuth credentials from env first, then disk as a fallback."""
    if token_secret_env:
        raw_token = os.getenv(token_secret_env, "").strip()
        if raw_token:
            token_info = json.loads(raw_token)
            with open(token_file, "w") as token:
                token.write(json.dumps(token_info))
            print(f"  [INFO] Restored YouTube OAuth token from ${token_secret_env}.")
            return Credentials.from_authorized_user_info(token_info, SCOPES)

    if os.path.exists(token_file):
        return Credentials.from_authorized_user_file(token_file, SCOPES)

    return None

# Pinned comment templates (forces engagement = algorithm boost)
PIN_COMMENTS = [
    "🙏 जय श्री राम! कमेंट में 'जय श्री राम' लिखो — भगवान तुम्हारी हर मनोकामना पूरी करेंगे! 🙏\n\n👉 SUBSCRIBE करो, रोज़ नई भक्ति वीडियो आएगी!",
    "🔱 हर हर महादेव! टाइप करो 'ॐ नमः शिवाय' — आज का दिन शुभ हो जाएगा!\n\n👉 SUBSCRIBE करो और बेल 🔔 दबाओ!",
    "🙏 भगवान देख रहे हैं! इस वीडियो को LIKE ❤️ करो और 3 लोगों को SHARE करो — पुण्य मिलेगा!\n\n👉 SUBSCRIBE for daily Bhakti! 🙏",
    "💛 राधे राधे! अगर कृष्ण जी पर विश्वास है तो 'राधे राधे' लिखो! 🙏\n\n👉 रोज़ सुबह 5 बजे नई वीडियो — SUBSCRIBE करो!",
    "⚡ जय बजरंगबली! शेयर करो और देखो चमत्कार! 🙏\n\n👉 SUBSCRIBE = रोज़ भक्ति का डोज़! 🔔",
]

def get_authenticated_service(token_file="token.json", token_secret_env=None, client_secret_file="client_secret.json"):
    """Handles OAuth 2.0 authentication for YouTube API."""
    creds = _load_credentials(token_file, token_secret_env=token_secret_env)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"  Refreshing YouTube OAuth token for {token_file}...")
            try:
                creds.refresh(Request())
            except RefreshError as e:
                raise RuntimeError(
                    f"YouTube token refresh failed for {token_file}: {e}. "
                    "The refresh token is likely revoked/expired or the OAuth client changed. "
                    f"Re-authorize this channel and update {token_file}"
                    + (f" / ${token_secret_env}" if token_secret_env else "")
                    + "."
                ) from e
        else:
            print(f"  First time auth required for {token_file}. Please sign in.")
            if not os.path.exists(client_secret_file):
                raise FileNotFoundError(
                    f"'{client_secret_file}' not found! "
                    "Download it from Google Cloud Console > APIs > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, "w") as token:
            token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def post_pinned_comment(youtube, video_id, comment_text=None):
    """Posts and pins an engagement-boosting comment on the uploaded video."""
    comment_text = comment_text or random.choice(PIN_COMMENTS)
    try:
        # Post comment
        comment_response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        
        comment_id = comment_response["snippet"]["topLevelComment"]["id"]
        print(f"  [OK] Pinned engagement comment posted!")
        return comment_id
    except Exception as e:
        print(f"  [WARN] Comment failed (not critical): {e}")
        return None

def upload_video(
    video_path,
    title,
    description,
    tags_str,
    youtube=None,
    token_file="token.json",
    token_secret_env=None,
    client_secret_file="client_secret.json",
    category_id="22",
    default_language="hi",
    default_audio_language="hi",
    pinned_comment_text=None,
    enable_pinned_comment=False,
):
    """Uploads a video to YouTube using a specific token file."""
    youtube = youtube or get_authenticated_service(
        token_file=token_file, 
        token_secret_env=token_secret_env, 
        client_secret_file=client_secret_file
    )

    # Clean hashtags into a list of words
    tags = [t.strip().replace("#", "") for t in tags_str.split() if t.startswith("#")]

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:15],
            "categoryId": category_id,
            "defaultLanguage": default_language,
            "defaultAudioLanguage": default_audio_language,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"  Starting YouTube upload for '{title[:50]}'...")
    response = None
    
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  Upload {pct}% complete...")
        except Exception as e:
            print(f"  [ERROR] Upload paused or failed! Retrying... {e}")
            break

    if response:
        video_id = response.get("id", "unknown")
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  [OK] Successfully uploaded! Link: {video_url}")
        if enable_pinned_comment:
            post_pinned_comment(youtube, video_id, comment_text=pinned_comment_text)
        
        return video_id
        
    return None

if __name__ == "__main__":
    print("YouTube uploader module loaded.")
