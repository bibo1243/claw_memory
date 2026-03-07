#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse

# Using the credentials provided by the user in message 414
CLIENT_ID = "[MASKED_CLIENT_ID].apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-[MASKED_CLIENT_SECRET]"
REDIRECT_URI = "http://localhost:8080/" 
CODE = "4/0AfrIepBYwkKh5DOtnR5LKaqA6QiqP4S_92moktuMikoBjc_lB5LdlHZifdVhfpsJRDQaaw"

def exchange_code():
    data = urllib.parse.urlencode({
        'code': CODE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }).encode('utf-8')

    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.load(resp)
            print(json.dumps(resp_data))
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == "__main__":
    exchange_code()
