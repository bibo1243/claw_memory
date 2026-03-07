#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

# Load .env manually
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    os.environ[parts[0]] = parts[1]

# Go up 4 levels: skills/google-calendar/scripts/ -> workspace/.env
load_env(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env')))

def refresh():
    # Hardcode credentials from MEMORY.md directly
    client_id = "[MASKED_CLIENT_ID].apps.googleusercontent.com"
    client_secret = "GOCSPX-[MASKED_CLIENT_SECRET]"
    refresh_token = "1//[MASKED_REFRESH_TOKEN]"

    print(f"DEBUG: Using hardcoded creds for refresh...")

    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }).encode('utf-8')
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.load(resp)
            print(json.dumps(resp_data))
            return resp_data['access_token']
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == '__main__':
    refresh()
