---
name: notion-integration
description: 整合 Notion 功能，支援新增任務、記帳、知識庫。當使用者想要「新增任務」「記帳」「筆記」或提到 Notion 時使用。
---

# Notion 整合

此技能提供與使用者 Notion 資料庫的互動功能。

## 設定

環境變數（存於 `.env`）：
- `NOTION_TOKEN`: API Token
- `NOTION_DB_TASKS`: 每日行動資料庫 ID
- `NOTION_DB_TRANSACTIONS`: 記帳明細資料庫 ID
- `NOTION_DB_KNOWLEDGE`: 知識庫資料庫 ID

## 功能

### 1. 新增任務 (Tasks)
將待辦事項新增至「Tasks (每日行動)」資料庫。
- 欄位：Name (標題), Status (狀態), Do Date (執行日期), Context (情境), Priority (優先級)

### 2. 記帳 (Transactions)
將消費記錄新增至「Transactions (記帳明細)」資料庫。
- 欄位：Item (項目), Amount (金額), Category (分類), Date (日期)

### 3. 新增筆記 (Knowledge Base)
將對話重點或筆記存入「Knowledge Base (知識庫)」。
- 欄位：Name (標題), Type (類型: Note/SOP/Course), Tags (標籤), Content (內容)

## 使用範例

- 「幫我新增一個任務：明天下午開會」
- 「午餐吃了 150 元」
- 「把剛剛討論的重點存到 Notion 筆記」
