# TickTick 技能開發規格書 (TickTick Skill Spec)

## 1. 專案目標
為 Gary 的 OpenClaw 助理開發一套 **TickTick 整合技能**，使助理能夠透過 API 直接管理 Gary 的待辦事項、清單與專案進度，實現「單一介面管理多平台任務」的目標。

## 2. 核心功能需求

### A. 任務管理 (Task Management)
- **新增任務**：透過對話指令（如：「提醒我明天買牛奶」）快速新增任務。
- **查詢任務**：列出特定清單（如：「今日待辦」）或特定標籤的任務。
- **完成任務**：標記任務為「已完成」。
- **修改任務**：更新任務標題、截止日期或優先級。

### B. 清單與分類 (Lists & Organization)
- **清單同步**：讀取 Gary 帳號下所有的清單（Inbox, Work, Personal 等）。
- **指定清單**：新增任務時可指定放入特定清單。
- **標籤支援**：支援讀取與設定任務標籤 (Tags)。

### C. 提醒與排程 (Reminders & Scheduling)
- **日期與時間**：支援自然語言設定截止日期（如：「下週三下午兩點」）。
- **重複任務**：支援設定重複規則（如：「每週一」）。

## 3. 技術需求與 API 整合

### A. TickTick Open API
- **官方文件**：[TickTick Open API Documentation](https://developer.ticktick.com/docs)
- **認證方式**：OAuth 2.0
  - 需要 Client ID
  - 需要 Client Secret
  - 需要 Redirect URI

### B. 開發流程
1. **申請開發者帳號**：Gary 需至 [TickTick Developer Center](https://developer.ticktick.com/manage) 註冊應用程式。
2. **獲取憑證**：取得 `Client ID` 與 `Client Secret`。
3. **授權流程**：助理生成授權連結 -> Gary 點擊同意 -> 助理取得 `Access Token`。
4. **API 實作**：助理根據 API 文件撰寫 Python 腳本 (ticktick_skill.py)。

## 4. 安全性考量
- **Token 儲存**：Access Token 與 Refresh Token 需加密儲存於 OpenClaw 的 `secrets.env` 中。
- **權限範圍**：僅申請必要的讀寫權限 (Tasks: Write, Tasks: Read)。

## 5. 交付項目
- `ticktick_skill.py`：核心邏輯腳本。
- `SKILL.md`：技能使用說明文件。
- `auth_helper.py`：協助進行 OAuth 授權的工具腳本。

---

## 6. 下一步行動 (Action Items)

請 Gary 協助完成以下步驟，以便助理開始開發：
1.  前往 [TickTick Developer Center](https://developer.ticktick.com/manage) 登入。
2.  點擊 "New App" 建立新應用。
    - **App Name**: OpenClaw Assistant
    - **OAuth Redirect URL**: (暫時填寫) `http://localhost:8080`
3.  將產生的 **Client ID** 與 **Client Secret** 傳送給助理。
