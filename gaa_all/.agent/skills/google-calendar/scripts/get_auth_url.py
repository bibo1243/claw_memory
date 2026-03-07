#!/usr/bin/env python3
"""Generate OAuth authorization URL for Google Calendar"""
import os
import sys
import urllib.parse

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
if not CLIENT_ID:
    print("Error: GOOGLE_CLIENT_ID not set", file=sys.stderr)
    sys.exit(1)

SCOPES = 'https://www.googleapis.com/auth/calendar'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

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
