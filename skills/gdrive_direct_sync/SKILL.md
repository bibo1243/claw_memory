---
name: Google Drive Direct Sync Protocol
description: 處理 Google Drive 與本地端檔案同步的核心準則，繞過桌機版自動同步延遲問題，採「雲端直傳、取得連結、本地備份」三步流程。
---

# 核心觀念：Drive-First, Dual-Sync

當涉及到將文件（如 Inbox 歸檔、新建立的 md 檔、報表等）存儲並同步到 Google Drive 與本地資料夾，且需要放入 Notion 或 Things 3 追蹤時，**絕對不要依賴 macOS 的 Google Drive 桌面版自動同步**。因為繁雜的小檔案容易導致它掃描卡住，使雲端跟本地產生時間差。

必須嚴格執行以下 **「雲端直傳 👉 獲取連結 👉 本地歸檔」** 的三步工作流。

## 標準作業流程 (三步法)

### 1. 雲端優先直傳 (Cloud-First Creation & Upload)
- **判定目標 parent_id**：先確認該檔案/資料夾在 Drive 雲端上的目錄結構與 parent_id（如尚未建檔，則需先呼叫 API `POST` 建立資料夾）。
- **直傳檔案**：利用 Google Drive API（搭配 `gcloud auth print-access-token` 獲取 Token）直接將本地檔案透過 API 送上雲端。

### 2. 立刻獲取回傳連結 (Immediate Link Harvesting)
- API 直傳成功後，立刻解析回傳的 JSON 拿到 `webViewLink`。
- 這個連結**非常重要**：要直接提供給使用者，讓使用者可以直接貼進 Notion Goals DB 或 Tasks 裡作為永備連結。這保證了任何透過 Notion 連結點出去的項目一定是最新上傳的雲端版。

### 3. 本地端雙向落地 (Local Fallback Copy)
- 處理完雲端後，再將本地的整理對象 (`/Inbox/...` 等) `shutil.copy2` 複製到該放的本地個人資料夾路徑。
- 確保任何因解壓 (例如 epub) 或暫存處理產生的碎檔案，也必須**依據 <Safe Delete Policy>** 在本地清理乾淨或覆蓋，保持本地檔案結構清爽。

## Python 實作腳本參考
當你需要使用 Agent 執行此工作流，請參考此架構（已經實證可避免同步鎖死）：

```python
import os, json, subprocess, urllib.request, shutil

# 1. 取得 Token
TOKEN = subprocess.run(["/opt/homebrew/bin/gcloud", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()

# 2. 實作 API Catcher
def drive_api(method, url, data=None): ... # 帶 Bearer Token 呼叫
def upload_file(file_path, parent_id): ... # 使用 curl multipart POST 實作上傳

# 3. 三步法落地範例
# Step 1: 建立/尋找雲端資料夾
folder = find_or_create_folder("目標資料夾名稱", PARENT_ID)
folder_id = folder["id"]

# Step 2: 上傳並取得連結
res = upload_file("/path/to/local_file.pdf", folder_id)
print(f"🔗 共享連結: {res.get('webViewLink')}")

# Step 3: 本地落地並清理
shutil.copy2("/path/to/local_file.pdf", "/正確/本地/歸檔路徑/")
# shutil.rmtree("/錯誤的解壓縮/暫存目錄", ignore_errors=True) #清理垃圾
```

## 使用情境
- 當使用者要求「將 Inbox 資料歸檔，並給我 Notion 用的連結」。
- 當 Agent 自動生成了一份重要的 Report、Markdown 檔案（例如「年度願景信」），並需要妥善保存。
- 當使用者抱怨「Google Drive 網頁版沒有出現我剛放的檔案」時，立即以本 Skill 作為替代方案修復同步問題。
