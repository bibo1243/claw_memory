import urllib.request, json

token = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}

db_id = "30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2"
req = urllib.request.Request(f"https://api.notion.com/v1/databases/{db_id}", headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print("Properties:", list(data.get("properties", {}).keys()))
except Exception as e:
    print(f"Error fetching DB info: {e}")
