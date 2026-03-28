# Aura Shorts Engine

A fully automated YouTube Shorts building and uploading engine.

## Features
- Generates a script via Google Gemini (Free tier)
- Generates speech via Edge-TTS (Free)
- Fetches HD Background video clips via Pexels API (Free)
- Stitches the video, edits and generates VTT captions via MoviePy
- Uploads directly to YouTube via YouTube API.

## Setup
1. Duplicate `.env.example` to `.env` and fill the keys.
2. `pip install -r requirements.txt`
3. Download `client_secret.json` from Google Cloud Console matching your YouTube Content Owner/Channel APIs.
4. Run `python main.py` for testing. First run will prompt Google OAuth Login.
5. Setup GitHub Actions with Repository Secrets to deploy this as an autonomous script 24/7.
