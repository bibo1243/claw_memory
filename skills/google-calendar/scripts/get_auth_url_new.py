#!/usr/bin/env python3
"""Generate OAuth authorization URL for Google Calendar - Updated Client"""
import os
import sys
import urllib.parse

# Hardcoded new credentials from user
CLIENT_ID = "[MASKED_CLIENT_ID].apps.googleusercontent.com"
# Redirect URI: the user's client config has http://localhost:8080/
REDIRECT_URI = 'http://localhost:8080/' 

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive'
]

params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': ' '.join(SCOPES),
    'access_type': 'offline',
    'prompt': 'consent',
}

auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
print(auth_url)
