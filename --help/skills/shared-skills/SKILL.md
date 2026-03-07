---
name: shared-skills
description: 雙機協同核心：同步本地 Skills 到 Google Drive (gaa_all/.agent/skills)，讓雲端 Bot 可以下載並學習新能力。
---

# 共享技能 (Shared Skills)

此技能負責將本地的 `skills/` 目錄與 Google Drive 上的 `gaa_all/.agent/skills` 進行同步。這是 "GaaClaw" (地端) 與 "gaa1243" (雲端) 共享能力的關鍵通道。

## 功能

### 1. 推送技能 (Push)
- 指令：`shared-skills push <skill_name>` 或 `shared-skills push --all`
- 作用：將本地的指定 Skill（或全部）上傳到 Google Drive。
- 覆蓋規則：Drive 上的舊版本將被覆蓋。

### 2. 拉取技能 (Pull)
- 指令：`shared-skills pull <skill_name>` 或 `shared-skills pull --all`
- 作用：從 Google Drive 下載指定 Skill（或全部）到本地 `skills/`。
- 應用：雲端 Bot 啟動時或收到通知時執行，以獲取最新能力。

## 依賴
- Google Drive API (共用 `shared-memory` 的憑證與邏輯)
- `gaa_all` 資料夾權限

## 檔案結構
- `scripts/sync_skills.py`: 主程式，處理上傳/下載邏輯。
