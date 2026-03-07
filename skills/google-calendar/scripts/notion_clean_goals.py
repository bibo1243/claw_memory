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

def get_page_property(page_id, prop_name):
    url = f"{BASE_URL}/pages/{page_id}/properties/{prop_name}"
    return request('GET', url)

def delete_page(page_id):
    body = {
        'archived': True
    }
    url = f"{BASE_URL}/pages/{page_id}"
    request('PATCH', url, json.dumps(body).encode('utf-8'))

def clean_duplicate_goals(db_id):
    # 1. Get all goals
    body = {'sorts': [{'timestamp': 'created_time', 'direction': 'descending'}]} # Newest first
    data = request('POST', f"{BASE_URL}/databases/{db_id}/query", json.dumps(body).encode('utf-8'))
    
    seen_titles = {}
    
    for page in data.get('results', []):
        page_id = page['id']
        title_prop = page['properties']['Name']['title']
        title = title_prop[0]['text']['content'] if title_prop else "Untitled"
        
        # Check if has image
        has_image = False
        if 'Goal Image' in page['properties']:
            files = page['properties']['Goal Image']['files']
            if files:
                has_image = True
        
        if title in seen_titles:
            existing = seen_titles[title]
            
            # Logic: Keep the one with image, delete the other.
            # If both have images or neither, keep the newer one (current one in loop is newer due to sort? No, descending means newer first).
            # Wait, descending sort means first item is NEWER. 
            # We likely created duplicates later. The OLDER ones might be the ones we generated images for?
            # Or did we generate images for the NEW batch?
            # Let's check which one has image.
            
            if has_image and not existing['has_image']:
                # New one has image, old one doesn't. Keep new, delete old.
                print(f"Deleting duplicate '{title}' (ID: {existing['id']}) - No image")
                delete_page(existing['id'])
                seen_titles[title] = {'id': page_id, 'has_image': True}
            elif not has_image and existing['has_image']:
                # Old one has image, new one doesn't. Delete new.
                print(f"Deleting duplicate '{title}' (ID: {page_id}) - No image")
                delete_page(page_id)
                # Keep existing in dict
            else:
                # Both have image or neither. Delete the newer one (duplicate).
                # Since we iterate descending, the current 'page' is newer.
                # But wait, usually we want to keep the one with content.
                # Let's assume the one with image is better. If both same, delete current (newer).
                print(f"Deleting duplicate '{title}' (ID: {page_id}) - Redundant")
                delete_page(page_id)
        else:
            seen_titles[title] = {'id': page_id, 'has_image': has_image}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_clean_goals.py <db_id>")
        sys.exit(1)
        
    clean_duplicate_goals(sys.argv[1])
    print("Cleanup complete.")
