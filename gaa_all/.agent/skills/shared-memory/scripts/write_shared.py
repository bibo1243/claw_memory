#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
from datetime import datetime

# Load .env
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Placeholder until we integrate Drive API
SHARED_FILE = "/home/node/.openclaw/workspace/gaa_all/對話.md"

def write_shared(bot_name, message):
    if not os.path.exists(os.path.dirname(SHARED_FILE)):
        os.makedirs(os.path.dirname(SHARED_FILE))
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {bot_name}: {message}\n"
    
    with open(SHARED_FILE, 'a') as f:
        f.write(line)
    
    print(f"Recorded: {line.strip()}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 write_shared.py <bot_name> <message>")
        sys.exit(1)
        
    bot_name = sys.argv[1]
    message = sys.argv[2]
    write_shared(bot_name, message)
