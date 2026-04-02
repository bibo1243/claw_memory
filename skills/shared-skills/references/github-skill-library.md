# GitHub 共用 Skill 庫規範

這份參考檔定義 `claw_memory` repo 如何作為所有 agent 的共用 skill 庫。

## Canonical source

- Repo: `https://github.com/bibo1243/claw_memory.git`
- Canonical directory: `skills/`

## 目標

- VS Code 裡的 Kimi / Codex 共用同一套 skill
- Trae 裡的 Kimi / MiniMax 共用同一套 skill
- 另一台電腦 clone 同一個 repo 後，也能得到同一套 skill

## 建議掛載方式

優先順序：

1. symlink
2. `scripts/sync_git_skills.sh`
3. 手動複製

原因：

- symlink 最不容易漂移
- 同步腳本適合不支援 symlink 的 agent
- 手動複製最容易造成版本分叉

## 目錄規則

- 正式 skill 放在 `skills/<skill-name>/`
- 每個 skill 至少有 `SKILL.md`
- 需要 UI metadata 時放 `agents/openai.yaml`
- 可執行腳本放 `scripts/`
- 參考文件放 `references/`

## Agent 對接原則

- Codex: 將 agent 的本地 `skills/` 指向或同步到 repo 的 `skills/`
- VS Code 內的 agent: 若支援自定 skill path，直接指向 repo 的 `skills/`
- Trae: 若支援自定 skill path，直接指向 repo 的 `skills/`；否則用同步腳本
- OpenClaw / 其他 bot: 啟動前做 `git pull`，再同步到本地 skill 目錄

## 禁止事項

- 不要同時在兩台電腦改同一個 skill 後再靠雲端硬同步合併
- 不要把 OneDrive 當唯一權威來源
- 不要在 IDE 專屬 skills 目錄改完卻不回寫 GitHub repo

## 最小同步命令

```bash
./skills/shared-skills/scripts/sync_git_skills.sh ~/.codex/skills
```

把 `~/.codex/skills` 換成目標 agent 的 skill 目錄即可。
