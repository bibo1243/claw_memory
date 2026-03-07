import urllib.request, json

NOTION_TOKEN = 'ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR'

req = urllib.request.Request('https://api.notion.com/v1/search', method='POST')
req.add_header('Authorization', f'Bearer {NOTION_TOKEN}')
req.add_header('Notion-Version', '2022-06-28')
req.add_header('Content-Type', 'application/json')

data = {
    'query': 'Tasks',
    'filter': {
        'value': 'database',
        'property': 'object'
    }
}

try:
    with urllib.request.urlopen(req, data=json.dumps(data).encode()) as f:
        print(f.read().decode())
except Exception as e:
    print(e)
