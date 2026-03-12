import os, urllib.request, json
d={}
try:
    with open('.env') as f:
        for l in f:
            if '=' in l and not l.startswith('#'):
                k,v=l.strip().split('=',1)
                os.environ[k.strip()]=v.strip().strip("'\"")
except: pass

req = urllib.request.Request(
    "https://api.notion.com/v1/databases/30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2/query", 
    headers={
        "Authorization": f"Bearer {os.environ.get('NOTION_TOKEN')}", 
        "Notion-Version": "2022-06-28", 
        "Content-Type": "application/json"
    }, 
    method='POST'
)

res = json.loads(urllib.request.urlopen(req).read().decode())
print("=== 未完成待辦事項 ===")
for r in res.get('results', []):
    p = r['properties']
    n = p['名稱']['title'][0]['plain_text'] if p['名稱']['title'] else 'Empty'
    s = p.get('狀態', {}).get('select') or {}
    s_name = s.get('name', 'None')
    if s_name not in ['✅ 完成', '完成', 'Done', 'Archive', '取消', 'Archive ']:
        print(f"[{s_name}] {n}")
