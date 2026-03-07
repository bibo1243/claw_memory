#!/usr/bin/env python3
import urllib.parse

CLIENT_ID = "[MASKED_CLIENT_ID].apps.googleusercontent.com"
REDIRECT_URI = "http://localhost:8080/"
SCOPE = "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/drive"

params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPE,
    "access_type": "offline",
    "prompt": "consent"
}

url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
print(url)
