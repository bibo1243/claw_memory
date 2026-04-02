---
name: shared-skills
description: 多 IDE / 多電腦協同核心：以 GitHub repo 的 skills/ 作為唯一來源，同步到各 agent 的本地技能目錄，避免 VS Code、Codex、Trae、OpenClaw 各自漂移。
---

# 共享技能 (Shared Skills)

此技能負責維護共用 skill 技能庫，並將 GitHub repo 中的 `skills/` 同步到不同 IDE / agent 的本地技能目錄。

目前的權威來源是：

- GitHub repo: `https://github.com/bibo1243/claw_memory.git`
- Canonical path: repo root 下的 `skills/`

## 核心規則

1. 不要在多個 IDE 的本地 skill 目錄各自直接手改。
2. 所有正式 skill 都先改 GitHub repo 裡的 `skills/<skill-name>/`。
3. 各 agent 只做 `pull` 後同步，或用 symlink 掛到 repo。
4. 若某個 agent 不支援 symlink，就用同步腳本覆蓋本地 skill 目錄。
5. 若某個 skill 僅屬某一平台，仍可放在同一 repo，但需在 `SKILL.md` 裡寫清楚適用平台。

## 推薦流程

### 1. 編輯

- 在 GitHub repo 的 `skills/` 內新增或修改 skill。
- skill 至少要有 `SKILL.md`；需要 UI metadata 時加 `agents/openai.yaml`。

### 2. 發布

- commit
- push 到 GitHub

### 3. 其他 agent / 其他電腦同步

- 在本機 clone `claw_memory`
- 執行 `scripts/sync_git_skills.sh <target-dir>`
- 或把 agent 的 skills 目錄直接 symlink 到 repo 的 `skills/`

## 先讀這個

在操作前，先讀 [references/github-skill-library.md](references/github-skill-library.md)。

若要直接同步，請使用 [scripts/sync_git_skills.sh](scripts/sync_git_skills.sh)，不要每個 IDE 手動複製。
