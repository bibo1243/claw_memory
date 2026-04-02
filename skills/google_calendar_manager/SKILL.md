---
name: Google Calendar Manager
description: 透過 Google Calendar MCP 讀寫使用者的 Google 行事曆。涵蓋帳號資訊、主要行事曆 ID、可用工具與調用慣例。
---

# Google Calendar Manager（行事曆管理）

## 帳號與連線資訊
- **Google 帳號**: `bibo1243@gmail.com`
- **OAuth 憑證路徑**: `/Users/leegary/.gemini/gcp-oauth.keys.json`
- **MCP Server**: `@cocal/google-calendar-mcp`（設定於 `/Users/leegary/.gemini/antigravity/mcp_config.json`）
- **Token 模式**: Production（不需每週重新認證）
- **時區**: `Asia/Taipei`

## 主要行事曆（優先使用這兩個）

| 行事曆 | Calendar ID | 用途 |
|--------|-------------|------|
| ⭐ **冠葦行程** | `primary`（即 `bibo1243@gmail.com`） | 個人行程、會議、提醒 |
| 🏛️ **慈光暨附設機構** | `1383fae5b7204ef46d5fd09f338244740bff7449da5f137ea9fdb9a9f0a1d4de@group.calendar.google.com` | 機構活動、公務行程 |

> ⚠️ 除非使用者明確要求，否則預設只查詢上述兩個行事曆。

## 其他行事曆（需要時可查詢）

| 行事曆 | Calendar ID | 權限 |
|--------|-------------|------|
| 人資培訓（行政） | `suaviad0g2ahjk561jepnu1mk0@group.calendar.google.com` | 擁有者 |
| 人資業務 | `8dcdb1e024fda435ef2a712ebac8c4a9cd1e34d0cf24fa6eb5efb84c32eb9527@group.calendar.google.com` | 擁有者 |
| 庶務股行事曆 | `a09ef5a2ff0c04839aff548211482d16b7daa842f107627615703e41598c4c71@group.calendar.google.com` | 擁有者 |
| 庶務-港博 | `228108186c71c75393b45deedf630df229940d21897b229f1eb032eca2736e78@group.calendar.google.com` | 擁有者 |
| 庶務-紀騰 | `tiger.bodhi@gmail.com` | 擁有者 |
| 培訓（人事） | `kp3k35f932cjptq89f1nq1s43o@group.calendar.google.com` | 擁有者 |
| 慈馨 | `tch3300@gmail.com` | 擁有者 |
| 員工生日 | `lcubdf2bcm8pkf1bd1ihe7gq90@group.calendar.google.com` | 檢視 |
| 庶務-羅叔 | `dbdc1bd15f28733006181c887264e9c595b0ea76a371e114545970e1c5da3d2e@group.calendar.google.com` | 檢視 |
| 庶務-謝阿姨 | `a4d349932f4ec9a1f8a3ff7ee95e6508d0ef60e855b2d9e916116451ffe6c73a@group.calendar.google.com` | 檢視 |
| 庶務-銘澤 | `a80e8a4ca1da59f06afdd5c536d6a2a1a41489cfb2773d9c1405aea2cfa937a4@group.calendar.google.com` | 檢視 |
| 空間借用表 | `6f285da8962cce9c9b4e675861be14bdbfd69897385f1a63893f859ae013eae9@group.calendar.google.com` | 檢視 |
| 行政-行事曆 | `bc409c090282f941256cee43f6dfb96943db998c41fd6af7b19979105473f22b@group.calendar.google.com` | 檢視 |
| 台灣的節慶假日 | `zh-tw.taiwan#holiday@group.v.calendar.google.com` | 檢視 |

## 可用 MCP 工具

| 工具 | 用途 |
|------|------|
| `list-calendars` | 列出所有行事曆 |
| `list-events` | 列出指定時間範圍的事件 |
| `get-event` | 取得單一事件詳情 |
| `search-events` | 以關鍵字搜尋事件 |
| `create-event` | 建立新事件 |
| `update-event` | 修改事件 |
| `delete-event` | 刪除事件 |
| `get-freebusy` | 查詢忙碌/空閒時段 |
| `get-current-time` | 取得目前時間 |
| `list-colors` | 列出可用的事件顏色 |
| `respond-to-event` | 回應邀請（接受/拒絕/暫定） |
| `manage-accounts` | 管理多個 Google 帳號 |

## 調用慣例

### 1. 查詢行程時
- 必須提供 `timeMin` 和 `timeMax`（ISO 8601 格式）
- 時區一律用 `Asia/Taipei`
- 預設查「冠葦行程」（`primary`），除非使用者指定其他行事曆

### 2. 建立行程時
- `calendarId`: 預設 `primary`，除非使用者指明放到慈光
- `start` / `end`: ISO 8601 格式，例如 `2026-03-01T14:00:00`
- `timeZone`: `Asia/Taipei`
- 建立前主動確認：「要建在『冠葦行程』還是『慈光暨附設機構』？」

### 3. 搜尋行程時
- 使用 `search-events` 並提供 `query` 關鍵字
- 如果使用者沒指定時間範圍，預設搜尋最近 3 個月

### 4. 與 Things GTD Manager 整合
- 當 `@@` 任務包含明確的日期/時間，可以**同時**建立 Things 3 任務和 Google Calendar 事件
- 需先詢問使用者是否要同步到行事曆
