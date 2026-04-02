# Gaa 版規與原則 (2026-04-02 更新)

## 1. 雙機協同架構
- **@gaa_macbook_air_bot**: 運行於 MacBook Air (地端)。
- **@gaa1243_bot**: 運行於 Zeabur (雲端 / 本體)。
- **共享機制**: 記憶可各自持有，但技能統一以 GitHub repo `claw_memory/skills` 為唯一來源。
- **同步方式**: 各 IDE / agent 以 symlink 或 `skills/shared-skills/scripts/sync_git_skills.sh` 同步技能。

## 2. 回覆規則 (靜默模式)
- **有 @ 名字才回覆**：若訊息未提及機器人名稱，一律保持沉默。
- **統一紀錄者**：未來的規則修訂與重要紀錄，統一由 **@gaa1243_bot** (Zeabur) 負責執行，避免雙重寫入造成資料衝突。

## 3. 紀錄原則
- **繁體中文**：所有 Skill 的文件與說明紀錄，必須使用繁體中文。

## 4. Skill 治理原則
- 正式 skill 一律放在 repo 根目錄的 `skills/`
- 不要在各 IDE 專屬目錄直接手改後不回寫 repo
- 跨電腦時先 `git pull`，再做本地同步
