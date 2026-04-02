---
name: Skill Directory Manager
description: 負責維護「Agent Skills 總目錄表」。只要有新增、刪除或修改任何 Skill，必須確保同步更新 00_所有_Skill_說明目錄.md。
---

# Skill Directory Manager (技能目錄管理員)

## 📌 Context
Agent 系統中存在大量的英文命名的 Skill 資料夾，為了方便使用者 (Gary) 快速查找實際功能與對應中文說明，我們建立了一份 `@[/Users/leegary/個人app/.agent/skills/00_所有_Skill_說明目錄.md]` 作為目錄清單。

## 🎯 核心任務與觸發時機

1. **觸發時機**：當 Agent **建立 (Create)、修改 (Modify)、或是刪除 (Delete)** 了任何一個 Skill 的 `SKILL.md` 檔案時，**必須**自動觸發本任務。
2. **具體行動**：在處理完目標 Skill 的變更後，確保最後一步必須去更新 `@[/Users/leegary/個人app/.agent/skills/00_所有_Skill_說明目錄.md]` 中的表格欄位。

## ✨ 執行步驟 (SOP)
1. 確保新建立/修改的 Skill `SKILL.md` 的 YAML frontmatter 中有 `name` 與 `description`。
2. 使用 `replace_file_content` 工具，將該資料夾的名稱 (Folder)、中文名稱 (name) 與功能簡介 (description)、最後更新時間（YYYY-MM-DD），正確排入 `00_所有_Skill_說明目錄.md` 的 Markdown 表格中。
3. 如果是刪除技能，則將該筆資料從表格中移除。
