---
name: 4D Workflow Backend Architecture & Sync 
description: 負責維護 4D Workflow 的後端雙向同步機制，包含 Notion 與 Google Calendar 整合架構、資料過濾及樂觀更新 (Optimistic UI) 預想。
---

# 4D Workflow Backend Architecture 

## 1. 核心定位
此後端應用 (`4d-workflow-web/backend`) 扮演 4D 工作流的「神經中樞」，透過 Node.js/Express 服務隱藏底層 Notion 與 Google Calendar 的存取細節，並專注提供前端一個純粹基於 4D 模型 (Do it now, Delay it, Delegate it, Drop it) 的 RESTful API 介面。

## 2. 核心元件
我們設計了以下四大核心模組：
1. **NotionService**: 封裝官方 `@notionhq/client`。
   - 負責從 Notion 的「Tasks (每日行動)」資料庫中抓取所有未完成任務（透過 `狀態 !=完成` 過濾，確保效能與查詢精準度）。
   - 將 Notion 複雜的 Database Properties 對應至領域模型 `Task.ts`。
2. **GCalService**: 封裝官方 `googleapis` (`google.calendar`)。
   - 負責針對特定的時間段（如「硬性時間軸」任務）自動在主要日曆（`primary`）中建立區塊。
   - 將任務的完成狀態從前端同步至 Google 行事曆（如更改顏色 `colorId` 表示完成）。
3. **SyncOrchestrator**: 總管級的協調器。
   - 實現**樂觀派策略(Optimistic Approach)**，保證跨雙平台的邏輯一致性。
   - 操作流程範例 (Create Unified Task)：
     1. 首先將任務安全寫入 Notion（唯一真相來源 Single Source of Truth）。
     2. 檢查條件（是否具備排定時間且為 Do it now 或有具體時間的 Delay it），若符合，立刻呼叫 GCalService。
4. **SyncWorker**: 輪詢式背景常駐程式（Polling Mechanism）。
   - 保證當使用者從 Notion 官方 App 或 GCal App 移動或更改任務時，本地系統能察覺變動並同步進 4D 介面。

## 3. 金鑰與環境變數管理
專案運行高度依賴存在於後端 `.env` 檔案中的 OAuth/API 憑證。我們從本地 `.gemini/gcp-oauth.keys.json` 及 `.config/google-calendar-mcp` 取得了直接使用的 Google API 憑證，並從 `mcp_config.json` 取得了 Notion Integration Token。
* 需要的環境變數：
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REFRESH_TOKEN`
  - `PORT` (設定為 3001 以避開 Mac 系統的 Airplay Receiver Port 5000 佔用問題)

## 4. API 端點清單

| 方法 | 路由 | 功能說明 |
|------|------|---------|
| GET | `/api/health` | 健康檢查 |
| GET | `/api/tasks?view=工作任務` | 取得 Notion 任務（支援 view 篩選） |
| POST | `/api/tasks` | 建立 Notion 任務 |
| PUT | `/api/tasks/:id` | 更新 Notion 任務欄位 |
| DELETE | `/api/tasks/:id` | 封存（刪除）Notion 任務 |
| GET | `/api/gcal/calendars` | 取得 GCal 行事曆清單 |
| GET | `/api/gcal/events?date=&calendars=` | 取得指定日期的 GCal 事件 |
| PUT | `/api/gcal/events/:id` | 更新 GCal 事件（含跨行事曆搬移） |
| **POST** | **`/api/convert?direction=`** | **GCal ↔ Notion 互轉（搬移模式）** |

### `/api/convert` 端點說明
- **`direction=gcal_to_notion`**：GCal 事件 → Notion 任務
  - 必填 body: `gcalEventId`, `calendarId`, `title`, `date`, `time`, `duration`
  - 行為：在「Tasks (每日行動)」DB (`30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2`) 建立任務，然後刪除原本的 GCal 事件
- **`direction=notion_to_gcal`**：Notion 任務 → GCal 事件
  - 必填 body: `notionPageId`, `title`, `date`, `time`（無 time 則返回 400）
  - 行為：在 primary 行事曆（`bibo1243@gmail.com` / 冠葦行程）建立事件，然後封存 Notion 任務

> ⚠️ **注意**：此端點採**搬移 (Move)** 模式，原始資料會被刪除/封存，請勿重複呼叫。

## 5. 未來前端介接重點（Optimistic UI）
- 前端 (React / Vue) 應該在發出 `[PUT] /api/tasks/:id` 後**不等待 API 回應**，即可立刻在畫面上將卡片拖曳 / 顯示成功動畫。
- 背景處理如果遇到回傳錯誤（包含網路失敗），前端應該有一套重試與回滾 (Rollback) 畫面的機制，可參考 `.clarify/resolved/features/外部同步_與Notion或GCal同步失敗時的處理機制.md` 中規定的原則（本地佇列與標記異常重試燈號）。

## 6. 資料存取路徑
* 源碼位於 `/Users/leegary/個人app/4d-workflow-web/backend`
* 進入點：`src/api/server.ts`
* 啟動指令：`npm run dev`

## 7. 後端重啟 SOP（遇到服務掛掉時）
```bash
# 強制終止佔用 3001 port 的所有程序
lsof -ti:3001 | xargs kill -9 2>/dev/null

# 用 nohup + /dev/zero 正確啟動（避免 SIGTTIN 被 suspend）
nohup npm run dev < /dev/zero > /tmp/backend.log 2>&1 &

# 確認啟動成功
sleep 5 && curl -s http://localhost:3001/api/health
```
> 詳見 `vite_nohup_execution` Skill 的完整說明（前端也適用相同原則）。

