import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
PAGE_ID = '30e1fbf9-30df-8112-959c-c965f0099660'
INBOX_PAGE_ID = '30e1fbf9-30df-81e8-b538-f7302a74cdea'
SIGNIN_HEADING_ID = '30f1fbf9-30df-81ba-b446-f3885c5323c2'

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def api(endpoint, method='GET', data=None):
    url = f"https://api.notion.com/v1/{endpoint}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')}")
        return None

def get_taipei_time():
    utc_now = datetime.now(timezone.utc)
    return (utc_now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

# ── Step 1: Check inbox ──
print("1. Checking inbox...")
inbox_resp = api(f"blocks/{INBOX_PAGE_ID}/children")
inbox_items = []
if inbox_resp and inbox_resp.get('results'):
    for b in inbox_resp['results']:
        btype = b.get('type', '')
        # skip empty paragraphs
        if btype == 'paragraph':
            rt = b.get('paragraph', {}).get('rich_text', [])
            if not rt:
                continue
        inbox_items.append(b)

inbox_status = f"有 {len(inbox_items)} 則建議待審核" if inbox_items else "無新建議"
print(f"   Inbox: {inbox_status}")

# ── Step 2: Read page children, delete old sign-in ──
print("2. Cleaning old sign-in callouts...")
page_resp = api(f"blocks/{PAGE_ID}/children")
if page_resp:
    for block in page_resp.get('results', []):
        if block['type'] == 'callout':
            texts = "".join(t.get('plain_text', '') for t in block['callout'].get('rich_text', []))
            if '線上Gaa' in texts:
                print(f"   Deleting: {block['id']}")
                api(f"blocks/{block['id']}", method='DELETE')

# ── Step 3: Insert new sign-in callout ──
taipei_time = get_taipei_time()
content = f"[線上Gaa] {taipei_time}（台北時間 UTC+8）— ✅ 簽到完成。收件匣：{inbox_status}"
print(f"3. Inserting: {content}")

result = api(f"blocks/{PAGE_ID}/children", method='PATCH', data={
    "children": [{
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "icon": {"emoji": "☁️"},
            "color": "blue_background"
        }
    }],
    "after": SIGNIN_HEADING_ID
})

if result:
    print("✅ Check-in complete!")
else:
    print("❌ Failed to insert callout.")

# ── Step 4: If inbox has items, print them for review ──
if inbox_items:
    print("\n── 收件匣內容 ──")
    for i, item in enumerate(inbox_items, 1):
        btype = item.get('type', '')
        rt = item.get(btype, {}).get('rich_text', [])
        text = "".join(t.get('plain_text', '') for t in rt) if rt else "(no text)"
        print(f"  {i}. [{btype}] {text[:200]}")
