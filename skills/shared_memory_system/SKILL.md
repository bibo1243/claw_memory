---
name: 共享記憶系統
description: 多智能體協作的核心知識庫。管理技能註冊、經驗記錄、通訊機制，確保 Trae 與 Antigravity 等 AI 實例能共享知識與記憶。
---

# 🧠 共享記憶系統 (Shared Memory System)

## 📌 Context

這是 Gary 的 AI 多智能體協作系統核心。所有 AI 實例（Trae、Antigravity 等）共同維護一個中央知識庫，用於：

- 共享技能模組資訊
- 記錄重要經驗與解決方案
- AI 實例間的通訊與協調

## 🎯 核心任務

### 1. 讀取共享記憶
當需要查詢系統資訊、經驗記錄或技能時：
- 優先讀取中央知識庫：`/Users/leegary/個人app/Inbox/共享記憶.md`
- 技能模組：`/Users/leegary/個人app/.agent/skills/*/SKILL.md`
- 工作流程：`/Users/leegary/個人app/.agent/workflows/*.md`

### 2. 寫入新經驗
當完成重要任務或獲得關鍵學習時，使用結構化模板記錄：

```markdown
## 經驗記錄 [ID: EXP-YYYYMMDD-XXX]

### 問題描述
-

### 解決方案
-

### 執行結果
- 狀態：✅ 成功 / ⚠️ 部分成功 / ❌ 失敗
-

### 關鍵學習
-

### 相關技能
-

### 優先級
- [ ] P1 - 關鍵知識
- [ ] P2 - 重要參考
- [ ] P3 - 一般經驗
```

### 3. 通訊協調
AI 實例間的請求與回覆：

```markdown
## 📮 訊息佇列 [日期: YYYY-MM-DD]

### 待處理請求
| ID | 發送者 | 接收者 | 主題 | 狀態 |
|----|--------|--------|------|------|

### 已完成回覆
| ID | 發送者 | 主題 | 結果 |
|----|--------|------|------|
```

## ⚙️ 優先級定義

| 優先級 | 定義 | 保留期限 |
|--------|------|----------|
| **P1** | 關鍵知識（系統運作、核心準則） | 永久 |
| **P2** | 重要參考（常用技能、工作經驗） | 180 天 |
| **P3** | 一般經驗（一次性問題、臨時資訊） | 90 天 |

## 🔧 技術規範

### 檔案位置
- 中央知識庫：`/Users/leegary/個人app/Inbox/共享記憶.md`
- 技能模組：`/Users/leegary/個人app/.agent/skills/*/SKILL.md`
- 工作流程：`/Users/leegary/個人app/.agent/workflows/*.md`

### 同步協議
1. **讀取優先順序**：共享記憶.md > 技能模組 > 其他參考資料
2. **寫入規則**：完整模板 + 優先級標記
3. **衝突解決**：
   - 同一天多筆：合併至同一 ID
   - 技術細節：以最新日期者為準
   - 原則性衝突：保留雙方並標記需人工確認

## 📋 可用技能清單

當需要使用特定技能時，可從以下路徑調用：

| 技能 | 路徑 |
|------|------|
| Notion 工作區 | `.agent/skills/notion_workspace/SKILL.md` |
| 組織知識 | `.agent/skills/organization_knowledge/SKILL.md` |
| 會議協調 | `.agent/skills/core_meeting_coordinator/SKILL.md` |
| 會議記錄生成 | `.agent/skills/meeting_minutes_generator/SKILL.md` |
| Google 日曆 | `.agent/skills/google_calendar_manager/SKILL.md` |
| LINE 訊息讀取 | `.agent/skills/line_local_reader/SKILL.md` |
| 收件匣整理 | `.agent/skills/inbox_organizer/SKILL.md` |
| GTD 任務管理 | `.agent/skills/things_gtd_manager/SKILL.md` |
| 關鍵字管理 | `.agent/skills/keyword_manager/SKILL.md` |
| 工作日誌生成 | `.agent/skills/work_log_generator/SKILL.md` |
| 年度計畫檢查 | `.agent/skills/annual_plan_consistency/SKILL.md` |
| 目標檢視 | `.agent/skills/smart_goal_reviewer/SKILL.md` |
| 4D Workflow | `.agent/skills/4d_workflow_backend_architecture/SKILL.md` |
| 請假排班 | `.agent/skills/leave_schedule_reader/SKILL.md` |
| UI/UX 設計 | `.agent/skills/ui-ux-pro-max-skill-2.2.1/SKILL.md` |
| 技能目錄管理 | `.agent/skills/skill_directory_manager/SKILL.md` |

## ✨ 觸發時機

1. **系統初始化**：新 AI 實例加入時
2. **經驗記錄**：完成重要任務或獲得關鍵學習時
3. **技能查詢**：需要調用特定技能時
4. **跨實例通訊**：需要與其他 AI 協調時
5. **定期回顧**：每週檢視並更新共享記憶
