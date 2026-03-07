---
name: google-calendar
description: 透過 Google Calendar API 與 Google 日曆互動——列出即將到來的活動、建立新活動、更新或刪除活動。當需要從 OpenClaw 以程式方式存取日曆時使用此技能。
---

# Google 日曆技能

## 概述
此技能提供 Google Calendar REST API 的輕量級封裝。它可以讓你：
- **列出 (list)** 即將到來的活動（可選擇依時間範圍或查詢過濾）
- **新增 (add)** 一個新活動，包含標題、開始/結束時間、描述、地點和與會者
- **更新 (update)** 現有活動（透過 ID）
- **刪除 (delete)** 活動（透過 ID）

此技能使用 Python 實作 (`scripts/google_calendar.py`)。它預期設定以下環境變數（你可以使用 `openclaw secret set` 安全地儲存它們）：
```
GOOGLE_CLIENT_ID=…
GOOGLE_CLIENT_SECRET=…
GOOGLE_REFRESH_TOKEN=…   # OAuth 同意後取得
GOOGLE_CALENDAR_ID=primary   # 或特定日曆的 ID
```
第一次執行此技能時，可能需要執行 OAuth 流程以取得 refresh token——請參閱下方的 **設定** 章節。

## 指令
```
google-calendar list [--from <ISO> --to <ISO> --max <N>]
google-calendar add   --title <title> [--start <ISO> --end <ISO>]
                     [--desc <description> --location <loc> --attendees <email1,email2>]
google-calendar update --event-id <id> [--title <title> ... 其他欄位]
google-calendar delete --event-id <id>
```
所有指令都會將 JSON payload 列印到 stdout。錯誤會列印到 stderr 並導致非零的 exit code。

## 設定
1. **建立 Google Cloud 專案** 並啟用 *Google Calendar API*。
2. **建立 OAuth 憑證** (類型選擇 *Desktop app*)。記下 `client_id` 和 `client_secret`。
3. 執行輔助腳本以取得 refresh token：
   ```bash
   GOOGLE_CLIENT_ID=… GOOGLE_CLIENT_SECRET=… python3 -m google_calendar.auth
   ```
   它會開啟瀏覽器（或列印出你可以由其他地方開啟的 URL）並要求你授權存取。核准後，複製它列印出的 `refresh_token`。
4. 安全地儲存憑證：
   ```bash
   openclaw secret set GOOGLE_CLIENT_ID <value>
   openclaw secret set GOOGLE_CLIENT_SECRET <value>
   openclaw secret set GOOGLE_REFRESH_TOKEN <value>
   openclaw secret set GOOGLE_CALENDAR_ID primary   # 可選
   ```
5. 安裝必要的 Python 套件（一次性）：
   ```bash
   pip install --user google-auth google-auth-oauthlib google-api-python-client
   ```

## 運作原理 (簡述)
腳本從環境變數載入憑證，使用 refresh token 重新整理 access token，建立 `service = build('calendar', 'v3', credentials=creds)`，然後呼叫相應的 API 方法。

## 參考資料
- Google Calendar API 參考：https://developers.google.com/calendar/api/v3/reference
- 原生應用程式的 OAuth 2.0：https://developers.google.com/identity/protocols/oauth2/native-app

---

**注意：** 此技能不需要 GUI；它完全透過 HTTP 呼叫運作，因此適用於無頭伺服器 (headless servers)。
