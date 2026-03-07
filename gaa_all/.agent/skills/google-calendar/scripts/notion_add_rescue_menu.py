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

def add_rescue_menu(page_id):
    # Callout block for "Rescue Menu"
    # Inside, we can't create actual "Buttons" via API yet (Notion limitation), 
    # but we can create a visually distinct list of pages/links that act as triggers.
    
    blocks = [
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
    
    url = f"{BASE_URL}/blocks/{page_id}/children"
    return request('PATCH', url, json.dumps({'children': blocks}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_add_rescue_menu.py <page_id>")
        sys.exit(1)
        
    page_id = sys.argv[1]
    add_rescue_menu(page_id)
    print("Rescue Menu added.")
