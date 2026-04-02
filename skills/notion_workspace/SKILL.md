---
name: Notion Workspace & Core Rules
description: Gary 的 Notion 工作區架構、核心 DB ID、行為準則、任務管理規則、記帳規則。整合自線上Gaa 與 Macbook Air 兩份 MEMORY.md，去除重複後供 Antigravity 使用。
---

# Notion Workspace & Core Rules

> 整合來源：
> - 📋 MEMORY.md — 線上Gaa 核心記憶 (Notion: `30e1fbf9-30df-8121-8b91-fbdabbe7fffd`)
> - 📋 MEMORY.md — Macbook Air 核心記憶 (Notion: `30e1fbf9-30df-812e-91d9-d56bea4d62eb`)

---

## 📌 Notion 關鍵 DB / 頁面 ID

### 主要資料庫

| 資料庫 | Data Source ID | 用途 |
|--------|---------------|------|
| **Tasks (每日行動)** | `30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2` | 所有任務、工作記錄、靈感收集 |
| **Goals (目標)** | `30a1fbf9-30df-811f-ae48-df0df29ad7f9`（舊）/ `30a1fbf9-30df-81fb-93fa-000b651183d3`（新） | 目標管理 |
| **Transactions (記帳明細)** | `30a1fbf9-30df-81fa-91a1-d3e62216ac10` | 記帳 |
| **Skills DB** | `30b1fbf9-30df-81f1-897c-db2c1cb7fdb2`（線上Gaa）/ `30b1fbf9-30df-815f-926f-000b0f7919b0`（Air） | 技能庫 |
| **行政組業務追蹤系統** | `2531fbf9-30df-80fd-b257-e4338217e92c` | 去年以前的重要記錄與經驗 |
| **工作紀錄系統-冠葦** | `192185b5-6cfa-4626-8923-3f20b31376ab` | 個人工作紀錄（日期最新在上） |
| **線上修繕系統** | `28c1fbf9-30df-804a-893b-d4d0f6a6aded` | 修繕追蹤 |
| **109工作總表** | `6c99a12b-7746-448c-81b7-b20467de2f84` | 更早期的工作紀錄，重要經驗參考 |

### 關鍵頁面

| 頁面 | Page ID | 說明 |
|------|---------|------|
| discovery.md (GAA 規格書) | `30c1fbf9-30df-8149-861e-ed8d2f6a65ea` | 核心行為準則 |
| 近一個月的任務規劃 (1m) | `30d1fbf9-30df-81bb-9dc5-d6a2418dc5f3` | 當月任務彙整 |
| 小強升職記行動方案 | `06bf276d-4274-4f4d-9ec3-6b044ba542a7` | 任務規劃時優先參考 |
| shared-memory | `30c1fbf9-30df-81ff-a481-f505f3da4d2e` | 三機共享記憶 |
| 🧠 三機共享記憶 | `30e1fbf9-30df-8112-959c-c965f0099660` | 共享記憶索引 |
| 📮 記憶收件匣 | `30e1fbf9-30df-81e8-b538-f7302a74cdea` | Memory Inbox |

---

## ⚠️ 核心行為準則（來自 discovery.md）

1. **Move = Copy + Delete**：移動/隱藏資料時，確保原始位置已刪除，不可殘留
2. **隱私優先**：敏感功能預設建立在子頁面或隱藏區塊
3. **全繁體中文**：所有文件、Skill、說明必須使用繁體中文
4. **不忘初心 (Intentions Check)**：設定新目標/專案時，先檢視核心願景「靈魂擺渡者 — 渡人渡己、行雲流水」，若不符要主動提醒
5. **Notion 優先**：輕量檔案（<5MB）存 Notion。Drive = 冷儲存/大檔備份
6. **GTD 流程**：任務進來先走決策流程（要不要執行？→ 2分鐘？→ 專案/單步/行事曆）
7. **提醒附帶下一步行動**：每次提醒 Gary 任務時，必須附上具體的「下一步行動」，不能只說「記得做 X」

### 時區準則
- **Gary 在台灣台中，時區 = Asia/Taipei (UTC+8)**
- 絕對不可用 UTC 時間直接回覆
- 計算剩餘時間時，必須用台北時間

---

## 📝 任務管理規則

### 簡稱
- 「近一個月的任務規劃」= **1m**
- 「Tasks (每日行動)」= **task**

### Tasks DB 欄位（Gaa/Task 每日行動）
- **名稱** (title)
- **狀態** (select): 未開始 / Not started / Done
- **優先級** (select): 高 / 中 / 低
- **執行日期** (date)
- **情境** (multi_select): Work / Personal / 日精進
- **標籤** (multi_select): 追蹤 / 會議提案 / 組發會議 / 行政 / 靈感 ...
- **專案** (relation)
- **目標關聯** (relation)
- **照片** (files)

### Context 標籤
- Task DB Context **只有 Work / Personal / 日精進 三個**

### 追蹤任務規則
- 有「追蹤」標籤的任務，情境一律包含「工作」（Work）

---

## 💰 記帳規則

### 分類時段
| 分類 | 時間 |
|------|------|
| 早餐 | < 09:00 |
| 午餐 | 11:00 - 14:00 |
| 晚餐 | 16:30 - 19:00 |
| 點心/宵夜 | 其他時段 |

### 記帳 DB 欄位
- **Item** (title): 品名
- **Amount** (number): 金額
- **Date** (date): 日期
- **Category** (select): 分類
- **Receipt** (files): 收據照片
- **Note** (rich_text): 備註
- **Value Analysis** (select): 價值分析

### 記帳 DB ID
`30a1fbf9-30df-81fa-91a1-d3e62216ac10`

---

## 📂 參考資料位置

### Google Drive
| 項目 | 路徑/ID |
|------|---------|
| Root Folder | `gaa_all` |
| Memory Root | `gaa_all/memory`（ID: `1pIFY8B2g2h5AP7HVBG9jJR0gP-tjuhKm`） |
| Skills Root | `gaa_all/Agent_System/skills`（ID: `1MJaL3BzfM-pJeJazHCcKn5wwm4KdJIvG`） |
| 參考資料夾 | ID: `1gJ2J8-LyfdaA6vuk4NZBn6a87q6CjfjX` |
| 群組完整對話摘要 | `gaa_all/memory/gaa_party_summary.md`（ID: `1pE-W5Y_aMDkEamXN2xnLIvTPN_AC5w4m`） |

### 同事 LINE 對話備份
| 對象 | Drive 位置 |
|------|-----------|
| 整體資料夾 | `gaa_all/memory/與同事line對話/`（ID: `1fitOiODQ6flCfpzDALkwee9xIO1XzFVf`） |
| 梅芳 (白梅芳/Elizabeth Pai) | file ID: `1povVkz1Z3xb-U2K0oZ1HCFboZJiBuY--` |
| 梅芳 Email | elizabeth19720101@gmail.com |

---

## 🏢 重要名詞對照

| 簡稱/別名 | 正式名稱 | 說明 |
|-----------|---------|------|
| 組發會議 | 組織發展會議 | = 機構主管會議（三者同義） |

---

## 📊 日精進計數

- **公式**：Day X = 801 + (今天日期 - 2026-02-18).days
- **範例**：2026-02-28 = Day 801 + 10 = Day 811

---

## 📌 靈感收集流程

- Gary 對話中含「靈感」、洞察、反思、心得 → 記到 Notion Tasks DB，tag 設「靈感」
- 每日可彙整，Gary 再統整出日精進
- **不要自作主張直接寫日精進**

---

## 📌 工作對話自動記錄

- Gary 傳來的對話，若屬於工作相關 → Notion Tasks DB 新增一筆，Context = `Work`
- 同一話題延伸對話 → **不開新任務**，統合補充在同一筆記錄
- 內容要統合整理，不要東拼西湊

---

## 📊 Google Sheets 假表（排休表）

### 基本資訊
- **Sheet ID**: `1JnPLKg5HlKWfSymp79Yx66TZVYehBgVjU6ZbKQgaJR0`
- **連結**: `https://docs.google.com/spreadsheets/d/1JnPLKg5HlKWfSymp79Yx66TZVYehBgVjU6ZbKQgaJR0`

### 假表符號對照

| 符號 | 意義 |
|------|------|
| ◎ | 例假 |
| 〇 | 休息日 |
| ● | 特休（全天） |
| △ | 上午班 / 上午休 |
| ▽ | 下午休 |
| ▲ | 上午特休 |
| ▼ | 下午特休 |

### 假表結構（Row 對照）
- **Row 0**: 日期
- **Row 1**: 星期
- **Row 2**: 排假衝突
- **Row 5**: 兒早代理
- **Row 6**: Gary（B李冠葦）

### 查詢注意事項
- ⚠️ **分頁命名極不規則**，需暴力搜尋（不能靠固定命名規則）
- ⚠️ **日期起始不固定**（12/13/14/15/18 都有出現過）
- ⚠️ **假表會被人工修改**，不能假設資料是靜態的
- 同步到日曆後，必須雙向比對（Sheet→Cal 有沒有漏、Cal→Sheet 有沒有多）
- 日曆排休用 `colorId=9`（藍莓色）+ `transparency=transparent` 以區分其他行程

---

## 🚨 對外發送規則

- email、LINE、任何對外訊息 → **一律先擬稿給 Gary 看** → 確認 OK → 才發送
- **絕對不可自行發送**

---

## 📌 組織知識

- **發薪日**：每月 5 號（配合震旦系統，3/5 勞資會議通過，4/5 起適用）
- **宿舍施行細則 V7**：盤點責任下放→督導、清潔由資深員工主導、行政組→庶務股具體化

---

## 📌 優先順序框架

**時效性 × 影響力 = 優先級**

判斷問題：
1. 「今天不做明天會怎樣？」→ 判斷時效性
2. 「卡住幾個人？」→ 判斷影響力

隱藏原則：**先清小石頭**（先做完快速能完成的小任務）
