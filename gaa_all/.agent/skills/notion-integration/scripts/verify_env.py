#!/usr/bin/env python3
import os
import sys

# Load .env
def load_env(file_path):
    if not os.path.exists(file_path): return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

if __name__ == "__main__":
    if "NOTION_TOKEN" in os.environ:
        print("Notion token loaded successfully.")
    else:
        print("Notion token NOT found.")
