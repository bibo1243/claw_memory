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

def move_rescue_menu_to_subpage(root_page_id, subpage_title):
    # 1. Create the subpage "My Space"
    body = {
        'parent': {'page_id': root_page_id},
        'properties': {
            'title': [{'text': {'content': subpage_title}}]
        },
        'icon': {'emoji': '🔒'}
    }
    subpage = request('POST', f"{BASE_URL}/pages", json.dumps(body).encode('utf-8'))
    subpage_id = subpage['id']
    print(f"Created subpage '{subpage_title}' (ID: {subpage_id})")

    # 2. Add the Rescue Menu content to the subpage
    # Re-using the content structure from previous step
    menu_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "⚡ 能量急救菜單 (Energy Rescue)"}}],
                "color": "red_background"
            }
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "當衝動來襲時，不要思考，直接點選以下任一行動，轉移能量！"}}],
                "icon": {"emoji": "🛡️"},
                "color": "gray_background"
            }
        },
        {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "callout",
                                    "callout": {
                                        "rich_text": [{"type": "text", "text": {"content": "📝 自由寫作 (Writing)"}}],
                                        "icon": {"emoji": "✍️"},
                                        "color": "blue_background"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "callout",
                                    "callout": {
                                        "rich_text": [{"type": "text", "text": {"content": "🎤 忘我唱歌 (Singing)"}}],
                                        "icon": {"emoji": "🎵"},
                                        "color": "pink_background"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "callout",
                                    "callout": {
                                        "rich_text": [{"type": "text", "text": {"content": "💻 專注編程 (Coding)"}}],
                                        "icon": {"emoji": "💻"},
                                        "color": "orange_background"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "column",
                        "column": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "callout",
                                    "callout": {
                                        "rich_text": [{"type": "text", "text": {"content": "🧘 靈性分享 (Spirituality)"}}],
                                        "icon": {"emoji": "✨"},
                                        "color": "purple_background"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
    
    request('PATCH', f"{BASE_URL}/blocks/{subpage_id}/children", json.dumps({'children': menu_blocks}).encode('utf-8'))
    
    # 3. Clean up the root page (Delete the old visible blocks)
    # To delete, we need block IDs. Since we just appended them, getting the last few blocks of the page might work.
    # But for safety and simplicity via script, I'll just append a "Cleaner" message or let the user delete the old ones manually to avoid deleting wrong things.
    # Actually, I can list children and delete the ones that match our previous creation.
    
    print("Subpage created and populated. Please manually delete the old visible menu on the home page if it still exists.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_hide_menu.py <root_page_id>")
        sys.exit(1)
        
    root_page_id = sys.argv[1]
    move_rescue_menu_to_subpage(root_page_id, "My Space")
