import json
import os
import urllib.request
import urllib.error

# Load environment variables
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                k, v = line.split('=', 1)
                env[k] = v
    return env

env = load_env('/home/node/.openclaw/workspace/.env')
NOTION_TOKEN = env.get('NOTION_TOKEN')

if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN not found in .env")
    exit(1)

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
        print(f'HTTP error {e.code}: {e.read().decode()}')
        return None

def search_database(query):
    url = f"{BASE_URL}/search"
    body = {
        "query": query,
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    data = json.dumps(body).encode('utf-8')
    return request('POST', url, data)

def query_database(database_id):
    url = f"{BASE_URL}/databases/{database_id}/query"
    # Filter for Status = New
    body = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "New"
            }
        }
    }
    data = json.dumps(body).encode('utf-8')
    return request('POST', url, data)

# 1. Search for "LINE Inbox" database
print("Searching for 'LINE Inbox' database...")
search_results = search_database("LINE Inbox")

if not search_results or not search_results.get('results'):
    print("No database named 'LINE Inbox' found.")
    exit(0)

# Find exact match or best match
db_id = None
for result in search_results['results']:
    title_list = result.get('title', [])
    if title_list:
        title = "".join([t.get('text', {}).get('content', '') for t in title_list])
        if "LINE Inbox" in title:
            db_id = result['id']
            print(f"Found database: {title} (ID: {db_id})")
            break

if not db_id:
    print("Could not find exact match for 'LINE Inbox'.")
    exit(0)

# 2. Query for items with Status=New
print(f"Querying database {db_id} for New items...")
query_results = query_database(db_id)

if not query_results:
    print("Failed to query database.")
    exit(1)

results = query_results.get('results', [])
keywords = ["@All", "@李冠葦", "重要", "急", "核銷"]

print(f"Found {len(results)} items. Filtering...")

found_items = []

for page in results:
    props = page.get('properties', {})
    
    # Extract Message (Rich Text)
    message_prop_list = props.get('Message', {}).get('rich_text', [])
    message_text = "".join([t.get('text', {}).get('content', '') for t in message_prop_list])
    
    # Extract Sender (Title)
    sender_prop_list = props.get('Sender', {}).get('title', [])
    sender_text = "".join([t.get('text', {}).get('content', '') for t in sender_prop_list])
    
    # Check keywords (case-insensitive)
    search_text = (sender_text + " " + message_text).lower()
    
    # Add fullwidth @ variations to keywords
    keywords_lower = [k.lower() for k in keywords]
    
    is_important = any(k in search_text for k in keywords_lower)
    
    if is_important:
        found_items.append(f"- [{sender_text}] {message_text}")

if found_items:
    print("\n".join(found_items))
else:
    print("無")
