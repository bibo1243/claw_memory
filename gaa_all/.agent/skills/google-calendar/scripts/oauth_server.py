#!/usr/bin/env python3
"""Simple OAuth flow that prints the authorization URL and waits for the code"""
import os
import sys
import urllib.parse

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set", file=sys.stderr)
    sys.exit(1)

SCOPES = 'https://www.googleapis.com/auth/calendar'
# Use copy-paste redirect
REDIRECT_URI = 'https://developers.google.com/oauthplayground'

params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': SCOPES,
    'access_type': 'offline',
    'prompt': 'consent',
}

auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
print(auth_url)
