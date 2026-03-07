#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

# Load .env manually
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    os.environ[key] = value

load_env(os.path.join(os.path.dirname(__file__), '../../../../.env'))

def refresh():
    # Hardcode for debugging if env fails
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')

    print(f"DEBUG: ID={client_id[:5]}... Secret={client_secret[:5]}... Token={refresh_token[:5]}...")

    if not all([client_id, client_secret, refresh_token]):
        sys.stderr.write('Missing one of GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN\n')
        sys.exit(1)
        
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }).encode()
    
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    # req.add_header('Content-Type', 'application/x-www-form-urlencoded') # urllib adds this by default for POST data
    
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
