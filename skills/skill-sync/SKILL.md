---
name: skill-sync
description: 將本地 OpenClaw 技能 (SKILL.md) 同步到 Notion 資料庫。每當技能更新時執行此操作。
---

# 技能同步 (Skill Sync)

此技能將工作區中的所有 `SKILL.md` 檔案同步到使用者的 Notion "System Skills" 資料庫。

## 用法

```bash
python3 {workspace}/skills/google-calendar/scripts/sync_skills.py "30b1fbf9-30df-81f1-897c-db2c1cb7fdb2" "{workspace}"
```

(資料庫 ID 為了方便已硬編碼在技能定義中，但也可以作為參數傳遞)。

## 行為
- 掃描 `skills/*/SKILL.md`
- 從 frontmatter 解析 `name` 和 `description`
- 在 Notion 中 Upsert (建立或更新) 頁面
- 將完整的 Markdown 內容儲存在程式碼區塊中
