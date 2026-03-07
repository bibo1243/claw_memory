#!/usr/bin/env python3
"""
個人對話記錄腳本 (線上Gaa 版)
改編自 Macbook Air 的 personal_log_v2.py

使用方式：
  python3 personal_log_v2.py "Gary說的原文" "我回的內容"

設計原則：
1. 成對記錄 — 一次呼叫記兩條：Gary + 自己的回覆
2. 倒敘排列 — 新的在上面（prepend）
3. 自動建檔 — 每日一檔 YYYY-MM-DD (星期).md
4. 自動建資料夾 — GaaClaw_Memory 不存在會自動建
5. 如實記錄 — 不潤飾、不摘要、不添加贅詞
"""
import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# --- Configuration ---
MEMORY_ROOT_ID = "1pIFY8B2g2h5AP7HVBG9jJR0gP-tjuhKm"
INDIVIDUAL_FOLDER_NAME = "GaaClaw_Memory"
BOT_DISPLAY_NAME = "線上Gaa"
USER_DISPLAY_NAME = "Gary本尊"

# --- Helper: Load Env ---
def load_env(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    # 強制覆蓋，因為 Gateway 環境變數可能是舊的
                    os.environ[parts[0]] = parts[1]

load_env(os.path.join(os.path.dirname(__file__), '../../../.env'))

# --- Auth ---
def get_access_token(force_refresh=False):
    token = os.environ.get('GOOGLE_ACCESS_TOKEN')
    if token and not force_refresh:
        return token

    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing OAuth credentials.")
        sys.exit(1)

    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req) as resp:
            body = json.load(resp)
            new_token = body.get('access_token')
            if new_token:
                os.environ['GOOGLE_ACCESS_TOKEN'] = new_token
                return new_token
    except Exception as e:
        print(f"Token refresh failed: {e}")
        sys.exit(1)


def api_request(method, url, data=None, headers=None, retry=True):
    if headers is None:
        headers = {}
    headers['Authorization'] = f'Bearer {get_access_token()}'

    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            get_access_token(force_refresh=True)
            return api_request(method, url, data, headers, retry=False)
        if e.code == 404:
            return None
        print(f"HTTP Error {e.code}: {e.read().decode()[:200]}")
        return None


# --- Drive Helpers ---
def find_subfolder(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = api_request('GET', url)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None


def create_folder(parent_id, name):
    url = "https://www.googleapis.com/drive/v3/files"
    body = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    data = api_request('POST', url, data=json.dumps(body).encode('utf-8'))
    return data['id'] if data else None


def find_file(parent_id, name):
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    params = {'q': query, 'fields': 'files(id)'}
    url = f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}"
    data = api_request('GET', url)
    if data and data.get('files'):
        return data['files'][0]['id']
    return None


def read_file_content(file_id):
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8')
    except:
        return ""


def create_file(parent_id, name, content):
    url = "https://www.googleapis.com/drive/v3/files"
    meta = {'name': name, 'parents': [parent_id], 'mimeType': 'text/plain'}
    file_data = api_request('POST', url, data=json.dumps(meta).encode('utf-8'))
    if file_data:
        file_id = file_data['id']
        url_upload = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        api_request('PATCH', url_upload, data=content.encode('utf-8'),
                     headers={'Content-Type': 'text/plain'})
        return file_id
    return None


def update_file(file_id, content):
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
    api_request('PATCH', url, data=content.encode('utf-8'),
                 headers={'Content-Type': 'text/plain'})


# --- Main Logic ---
def get_today_filename():
    now = datetime.utcnow()
    # Convert to UTC+8
    import time
    utc_offset = 8 * 3600
    local_ts = time.time() + utc_offset
    local_dt = datetime.utcfromtimestamp(local_ts)
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday_str = weekdays[local_dt.weekday()]
    return f"{local_dt.strftime('%Y-%m-%d')} ({weekday_str}).md"


def get_timestamp():
    import time
    utc_offset = 8 * 3600
    local_ts = time.time() + utc_offset
    local_dt = datetime.utcfromtimestamp(local_ts)
    return local_dt.strftime("%H:%M")


def log_conversation(gary_said, my_reply):
    # 1. Find or create individual folder
    folder_id = find_subfolder(MEMORY_ROOT_ID, INDIVIDUAL_FOLDER_NAME)
    if not folder_id:
        print(f"Creating folder: {INDIVIDUAL_FOLDER_NAME}")
        folder_id = create_folder(MEMORY_ROOT_ID, INDIVIDUAL_FOLDER_NAME)

    # 2. Find or create today's file
    filename = get_today_filename()
    file_id = find_file(folder_id, filename)

    # 3. Format entry (成對記錄)
    ts = get_timestamp()
    entry = f"[{ts}] **{USER_DISPLAY_NAME}**: {gary_said}\n[{ts}] **{BOT_DISPLAY_NAME}**: {my_reply}\n\n---\n\n"

    if file_id:
        # Prepend (倒敘)
        current = read_file_content(file_id)
        updated = entry + current
        update_file(file_id, updated)
        print(f"✅ Prepended to {filename}")
    else:
        # Create new file
        header = f"# 對話記錄 ({filename})\n\n"
        create_file(folder_id, filename, header + entry)
        print(f"✅ Created {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python3 personal_log_v2.py "Gary說的原文" "我回的內容"')
        sys.exit(1)

    gary_said = sys.argv[1]
    my_reply = sys.argv[2]
    log_conversation(gary_said, my_reply)
