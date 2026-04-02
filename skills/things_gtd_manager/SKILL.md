---
name: Things GTD Manager
description: 處理包含 "@@" 觸發詞的任務訊息。採用 GTD (Getting Things Done) 方法論，透過 AppleScript 管理 Things 3 任務。
---

# Things GTD Manager (任務管理專家)

## 核心行為 (Core Behavior)
當使用者輸入訊息包含 `@@` 時，啟動以下流程：

### 1. 快速捕捉 (Quick Capture)
- 提取 `@@` 後方的所有文字作為「雜事 (Stuff)」。
- 判斷時間詞（如：下午三點、明天、3月5日）。
- 若含附件檔案，進入「參考資料處理流程」。

### 2. 相似任務智能比對 (Similar Task Deduplication & Merge)
在建立新任務前，必須先進行相似度檢索：
- **搜尋範圍**：檢索 Notion (`Gaa/Task` 每日行動) 與 Things 3 中是否有相似名稱或關鍵字的任務。
- **合併建議**：若發現高度相似或相關的現有任務，主動向使用者提出建議：「我發現 Notion/Things 3 中已有相似的任務『[任務名稱]』，請問是否要將這次的文字與附件連結**補充/合併**到該任務的備註中，而不是建立一個全新的任務？」
- **更新現有任務**：若使用者同意，則以追加 (Append) 的方式更新該任務的內容與備註，避免產生重複任務。
- **檔案處理原則 (⚠️ 絕對關鍵)**：
  - **位置判斷**：若檔案「已經」位於 `/Users/leegary/個人app/個人資料夾` 及其任何子目錄下，**不執行任何搬移動作**。
  - **歸類與清空 Inbox**：若檔案位於 `Inbox` 或其他非個人資料夾路徑，則「必須」主動觸發 [Inbox Organizer](../inbox_organizer/SKILL.md) 流程，將其搬移至 `個人資料夾`。
  - **落實「Inbox Zero」**：確保檔案最終位於 `個人資料夾` 下，且不在 `Inbox` 遺留。
  - **同步循環**：搬移完成（或確認已在個人資料夾）後，確保背景同步腳本已處理該檔案，並以其 Google Drive 連結進行後續 GTD 流程。

### 3. GTD 釐清詢問 (Clarify Task)
若確認為全新任務，在分析內容之後，視情況主動詢問使用者：
- 「這是一個複數步驟的『專案』嗎？要建立 Project 嗎？」
- 「這個任務是否有特定的標籤（Tag）？（例如：電腦、電話、採買）」
- 「是否要現在設定提醒時間？」

### 4. 參考資料處理流程（嚴格按順序執行）

當任務被判定為「參考資料」且包含附件時：

#### Step 1：取得檔案連結 (Google Drive)
- **檔案定位**：定位位於 `個人資料夾` 下的該檔案。
- **取得連結**：使用 Drive API 取得該檔案的分享連結。
- 連結格式：`https://docs.google.com/document/d/<FILE_ID>/edit` 或 `https://drive.google.com/file/d/<FILE_ID>/view`

#### Step 2：關鍵字分析
- 分析內容並提取 **5 個關鍵字**。
- 優先從 `Keyword Manager` 現有列表找尋。

#### Step 3：Notion 紀錄更新 (⚠️ **強制執行，不可跳過**)
- 於 Notion `Gaa/Task`（每日行動）新增或合併紀錄。
- **連結插入**：將 Step 1 的**檔案分享連結**貼在相關文字旁。

#### Step 4：Things 3 存檔 (⚠️ **暫停中，專注 Notion 與 Google Drive**)
- ~~在 Things 3 對應任務或新任務中，將 Step 1 的檔案分享連結寫入備註 (notes)。~~

> ⚠️ **關鍵原則**：所有 GTD 動作的前提是檔案位於「個人資料夾」中以確保持續同步與連結有效性。

### 🚨 雙向寫入防呆確認機制 (Double-Check Protocol)
在執行完上述流程後，**必須**在心中（Thought）自我檢查並於對話中宣告：
1. 「我是否已成功將資料寫入 Notion？」
2. ~~「我是否已成功將資料寫入 Things 3？」~~ (暫時取消確認)
**目前僅需於 Notion 寫入即可。**

### 5. AppleScript 常用指令參考
- `tell application "Things3" to make new to do with properties {name: "任務名稱", notes: "備註內容"}`
- `tell application "Things3" to to dos whose name contains "關鍵字"`

## 執行承諾
- 我會確保所有的任務輸入都精準對應到您的 Things 3。
- **嚴格遵守 Safe Delete Policy**。

## ⚠️ 踩坑記錄

### Notion 寫入檔案名稱必須附帶超連結
- **問題**：寫入 Notion 時，檔案名稱只寫了純文字，沒有附上 Google Drive 超連結。
- **原因**：只有部分檔案（如附件）做了上傳取連結，主要檔案遺漏。
- **規則（強制）**：寫入 Notion 的**每一個檔案名稱**，都**必須**附帶其 Google Drive 超連結。不論是主要文件（紀錄、議程、逐字稿）還是附件，全部都要有連結。在寫入 Notion 之前，先確認所有檔案都已上傳並取得連結。

### Notion Update Block API 限制
- **問題**：`update-a-block` 的 MCP tool 無法透過 `type` 參數更新 block 的 `rich_text` 內容。
- **解法**：改用「刪除舊 block → 用 `patch-block-children` + `after` 參數在正確位置重新插入」的方式。
