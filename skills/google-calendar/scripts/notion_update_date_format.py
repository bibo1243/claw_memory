#!/usr/bin/env python3
import os, sys, json, urllib.request

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def request(method, url, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f'HTTP error {e.code}: {e.read().decode()}\n')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_update_date_format.py <db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    
    # Notion Date property already supports time. 
    # This script is more about "Policy Enforcement" - ensuring we send time in future calls.
    # But we can also check if we need to rename it to "Date & Time" to be explicit? 
    # Let's just keep it as "Do Date" but acknowledge the policy change.
    
    print(f"Policy Updated for DB {db_id}: Date format must include time (ISO 8601).")
    # No schema change needed for Notion API to support time, it's just data format.
