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
# For now, we will simulate the file locally in shared workspace
SHARED_FILE = "/home/node/.openclaw/workspace/gaa_all/對話.md"

def read_shared(lines=20):
    if not os.path.exists(SHARED_FILE):
        return "No shared memory found."
    
    with open(SHARED_FILE, 'r') as f:
        content = f.readlines()
        return ''.join(content[-lines:])

if __name__ == "__main__":
    print(read_shared())
