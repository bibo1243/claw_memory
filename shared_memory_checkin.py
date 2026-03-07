import json
import urllib.request
import urllib.error
import datetime
import os

# Configuration
NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'
SHARED_MEMORY_PAGE_ID = '30e1fbf9-30df-8112-959c-c965f0099660'
INBOX_PAGE_ID = '30e1fbf9-30df-81e8-b538-f7302a74cdea'
SIGNIN_HEADING_ID = '30f1fbf9-30df-81ba-b446-f3885c5323c2'

# Headers
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def make_request(url, method="GET", data=None):
    try:
        req = urllib.request.Request(url, method=method, headers=HEADERS)
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    return make_request(url)

def delete_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    return make_request(url, method="DELETE")

def append_block_after(parent_id, after_id, block_data):
    # Correct API usage: append to parent, specify 'after'
    url = f"https://api.notion.com/v1/blocks/{parent_id}/children"
    payload = {
        "children": [block_data],
        "after": after_id
    }
    return make_request(url, method="PATCH", data=payload)

def check_inbox():
    # Check if inbox has any content (children)
    children_data = get_block_children(INBOX_PAGE_ID)
    if not children_data or not children_data.get('results'):
        return "無待處理建議"
    
    # Simple check: do we have any blocks?
    count = len(children_data['results'])
    if count > 0:
        return f"有 {count} 則建議待審核"
    return "無待處理建議"

def main():
    # 1. Calculate Taipei Time
    utc_now = datetime.datetime.utcnow()
    taipei_now = utc_now + datetime.timedelta(hours=8)
    time_str = taipei_now.strftime("%Y-%m-%d %H:%M")
    
    print(f"Current Taipei Time: {time_str}")

    # 2. Check Inbox Status
    inbox_status = check_inbox()
    print(f"Inbox Status: {inbox_status}")

    # 3. Find old '線上Gaa' check-in block
    # We need to scan the page's children to find the old callout to delete
    # Note: We are scanning the PAGE children, not the heading children (since headings don't have children)
    page_children = get_block_children(SHARED_MEMORY_PAGE_ID)
    
    old_block_id = None
    if page_children and 'results' in page_children:
        for block in page_children['results']:
            if block['type'] == 'callout':
                rich_text = block['callout'].get('rich_text', [])
                if rich_text:
                    plain_text = "".join([t.get('plain_text', '') for t in rich_text])
                    if '[線上Gaa]' in plain_text:
                        old_block_id = block['id']
                        # Assuming only one active check-in at a time, break after finding
                        break
    
    # 4. Delete old block if found
    if old_block_id:
        print(f"Deleting old check-in block: {old_block_id}")
        delete_block(old_block_id)
    else:
        print("No old check-in block found.")

    # 5. Create new Check-in Block
    new_block = {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": f"[線上Gaa] {time_str}（台北時間 UTC+8）— ✅ 簽到完成。收件匣：{inbox_status}"
                    }
                }
            ],
            "icon": {
                "type": "emoji",
                "emoji": "☁️"
            },
            "color": "blue_background"
        }
    }

    # 6. Insert new block AFTER the heading
    print(f"Inserting new check-in after heading: {SIGNIN_HEADING_ID}")
    result = append_block_after(SHARED_MEMORY_PAGE_ID, SIGNIN_HEADING_ID, new_block)
    
    if result:
        print("Check-in successful!")
    else:
        print("Check-in failed.")

if __name__ == "__main__":
    main()
