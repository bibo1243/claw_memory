#!/bin/bash
cd /home/node/.openclaw/workspace

# 設定身分
git config user.email "bot@openclaw.ai"
git config user.name "OpenClaw Bot"

# 將所有變更加入暫存區
git add .

# 如果有變更才進行 Commit 與 Push
if ! git diff-index --quiet HEAD --; then
    git commit -m "Auto-sync memory: $(date +'%Y-%m-%d %H:%M:%S')"
    # 先拉取雲端最新版本，避免衝突（採用 rebase 策略保持歷史乾淨）
    git pull origin main --rebase
    # 推送到 GitHub
    git push origin main
else
    echo "No changes to sync."
fi