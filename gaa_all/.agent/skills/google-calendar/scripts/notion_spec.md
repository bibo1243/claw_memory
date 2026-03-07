# Notion 系統規格書：自主人生戰略指揮中心 (Draft)

## 1. 核心理念
基於「易仁永澄」的目標管理與複利思維，打造一套 **「自主人生複利創造策略」** 的實踐系統。
系統不僅是管理待辦事項，更是 **Gary 的人生戰略指揮中心**，協助將長期意圖轉化為每日行動，並累積資本，實現複利成長。

## 2. 系統架構 (System Hierarchy)

本系統採用 **四層架構**，確保行動與願景一致：

### Layer 1: 意圖層 (Intentions & Vision) - *北極星*
- **Database**: `Intentions`
- **內容**: 長期願景、年度關鍵詞、人生使命。
- **功能**:
  - 定義「我想要成為什麼樣的人」。
  - 連結至 `Goals` (Layer 2)。

### Layer 2: 策略與目標層 (Strategies & Goals) - *戰略地圖*
- **Database**: `Goals` (目標) & `Projects` (專案)
- **內容**: 年度目標 (OKRs)、季度專案、關鍵成果。
- **功能**:
  - 將意圖拆解為可執行的專案。
  - 設定進度條 (Progress Bar) 追蹤完成度。
  - 關聯至 `Tasks` (Layer 3)。

### Layer 3: 執行層 (Execution & Action) - *每日戰場*
- **Database**: `Tasks` (待辦事項)
- **內容**: 每日行動清單、待辦事項、習慣追蹤。
- **功能**:
  - **Do Date**: 執行日期。
  - **Priority**: 優先級 (High/Medium/Low)。
  - **Status**: To Do / Doing / Done。
  - **Context**: 標籤 (Work, Personal, Study)。
  - **關聯**: 必須連結至一個 `Project` 或 `Goal`，確保每個行動都有意義。
  - **每日儀表板**: 只顯示「今日待辦」與「本週重點」。

### Layer 4: 資本與依靠層 (Assets & Support) - *軍火庫*
- **Database**: `Knowledge Base` (知識庫), `Finance` (財務 - 月度), `Transactions` (記帳明細), `Contacts` (人脈)
- **內容**:
  - **知識庫**: 讀書筆記、課程心得、SOP 文件。
  - **財務**: 月度財務報表與預算。
  - **記帳明細**: 每日消費記錄，含收據照片 (壓縮 < 300KB)。
  - **人脈**: 重要聯絡人管理。
- **功能**:
  - 累積經驗與資產，作為決策的依靠。
  - 支援標籤與搜尋，快速調用。

## 3. 關鍵功能模組 (Key Features)

### A. 行政中控台 (Admin Portal Dashboard)
- **首頁設計**:
  - **頂部**: 今日金句 / 年度關鍵詞 (提醒意圖)。
  - **左側**: 快速導航 (Quick Links)。
  - **中央**: 
    - **今日任務**: 過濾出 `Date = Today` 的任務。
    - **本週專案**: 顯示 `Status = In Progress` 的專案進度。
  - **右側**: 
    - **行事曆**: 嵌入 Google Calendar。
    - **財務概況**: 嵌入 Google Sheet 記帳圖表。

### B. 自動化同步 (Automation)
- **對話同步**: Gary 在 Telegram 對話中輸入「提醒我...」或「任務...」，自動新增至 `Tasks` Database。
- **行事曆同步**: Google Calendar 的會議自動同步至 Notion `Calendar View` (或透過 Embed 檢視)。

### C. 覆盤與日誌 (Review & Journal)
- **每日日誌**: 連結 `Tasks`，記錄今日成就、感恩事項與改進點。
- **每週覆盤**: 檢視本週 `Projects` 進度，調整下週計畫。

## 4. 下一步行動 (Action Items)

1.  **建立 Notion Workspace**: 
    - Gary 提供 Notion 帳號授權，或由助理建立模板連結供複製。
2.  **設定 Database**:
    - 依照架構建立 `Intentions`, `Goals`, `Projects`, `Tasks`, `Resources` 等資料庫。
3.  **開發整合工具**:
    - 撰寫 Python 腳本串接 Telegram 與 Notion API，實現對話新增任務功能。
