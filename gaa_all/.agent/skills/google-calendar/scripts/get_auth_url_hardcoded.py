#!/usr/bin/env python3
"""Generate OAuth authorization URL for Google Calendar"""
import os
import sys
import urllib.parse

# Hardcoded for reliability
CLIENT_ID = "[MASKED_CLIENT_ID].apps.googleusercontent.com"

SCOPES = 'https://www.googleapis.com/auth/calendar'
# Updated redirect URI for OAuth out-of-band flow (if deprecated, we might need a web server flow, but let's try this first)
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
