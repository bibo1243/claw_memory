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

def add_goal(db_id, title, category, description):
    body = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': title}}]},
            # 'Status': {'status': {'name': 'In progress'}}, # Removing Status as it might be 'Select' or missing
            'Category': {'select': {'name': category}}, 
        },
        'children': [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": description}}]}
            }
        ]
    }
    url = f"{BASE_URL}/pages"
    return request('POST', url, json.dumps(body).encode('utf-8'))

def add_category_prop(db_id):
    body = {
        'properties': {
            'Category': {
                'select': {
                    'options': [
                        {'name': 'Health', 'color': 'red'},
                        {'name': 'Work', 'color': 'blue'},
                        {'name': 'Finance', 'color': 'yellow'},
                        {'name': 'Family', 'color': 'pink'},
                        {'name': 'Social', 'color': 'orange'},
                        {'name': 'Learning', 'color': 'purple'},
                        {'name': 'Leisure', 'color': 'green'},
                        {'name': 'Challenge', 'color': 'gray'}
                    ]
                }
            }
        }
    }
    try:
        request('PATCH', f"{BASE_URL}/databases/{db_id}", json.dumps(body).encode('utf-8'))
    except:
        pass 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: notion_add_goals_batch.py <goals_db_id>")
        sys.exit(1)
        
    db_id = sys.argv[1]
    
    # 1. Update Schema
    add_category_prop(db_id)
    
    # 2. Add Goals
    goals = [
        ("戒色與意念淨化", "Health", "戒色：每兩週1次，只能射精1次，只能想著愛人。遇誘惑立馬停止意念不淨。"),
        ("健康生活作息", "Health", "每週5天23點前睡。過19:00不食。每週一日減食清腸(菜香耕)。不吃垃圾食物及零食。"),
        ("工作常規與督導", "Work", "每日如期繳交日誌。每月進行被督導一次。"),
        ("專案業務完成", "Work", "完成蔡小姐捐贈業務。完成蓮友慈益房子處理(出租/收租)。"),
        ("掃地僧課程AI化與股市分析", "Finance", "將掃地僧課程AI化，程式分析股市，虛擬系統練習投資。"),
        ("白銀出場策略", "Finance", "120鎂賣10%，200鎂賣20%，500鎂賣40%，剩30%留存。"),
        ("帶媽媽去金門廈門", "Family", "帶媽媽去金門、廈門走走。"),
        ("協助爸爸畫畫與線上分享", "Family", "跟爸爸學畫畫，協助老爸完成線上分享系統。"),
        ("深度社交與AI推廣", "Social", "每月一位夥伴深度交流。每月與主管(淑錡/紀騰)討論AI協助業務。"),
        ("AI軟體開發與閱讀", "Learning", "學習AI軟體開發(做內部系統/帶領元鼎)。每月讀一本書並記入知識庫。"),
        ("休閒旅遊計畫", "Leisure", "去桂林走走。每季看舞台劇。每月去山上走走。"),
        ("相聲短視頻挑戰", "Challenge", "將AI學習之路做成相聲短視頻並分享。")
    ]
    
    for title, cat, desc in goals:
        print(f"Adding goal: {title}...")
        add_goal(db_id, title, cat, desc)
        
    print("All goals added.")
