#!/bin/bash

# 切換到家目錄
cd ~

# 1. 確保先關閉舊的 cloudflared 隧道
pkill -f "cloudflared tunnel" || true

# 2. 清理舊的 log 檔案
rm -f ~/tunnel.log

# 3. 確保 Python CORS 代理程式正在執行 (監聽 Port 11435)
if ! lsof -i :11435 >/dev/null 2>&1; then
    echo "Starting Python CORS proxy..."
    nohup python3 ~/ollama_cors_proxy.py > ~/ollama_proxy.log 2>&1 &
    sleep 2
fi

# 4. 啟動 Cloudflare 隧道指向 Python 代理 (11435)
echo "Starting Cloudflare Tunnel..."
nohup ~/cloudflared tunnel --url http://127.0.0.1:11435 > ~/tunnel.log 2>&1 &

# 5. 迴圈等待並解析隨機分配的 trycloudflare.com HTTPS 網址 (最長等待 30 秒)
TUNNEL_URL=""
for i in {1..30}; do
    if [ -f ~/tunnel.log ]; then
        TUNNEL_URL=$(grep -oE "https://[a-zA-Z0-9-]+\.trycloudflare\.com" ~/tunnel.log | head -n 1)
        if [ ! -z "$TUNNEL_URL" ]; then
            break
        fi
    fi
    sleep 1
done

# 6. 如果成功取得網址，同步到 Zeabur 伺服器
if [ ! -z "$TUNNEL_URL" ]; then
    echo "Success! Tunnel URL is: $TUNNEL_URL"
    # 使用 curl 同步至 Zeabur (帶有 10 秒超時)
    SYNC_RES=$(curl -s --max-time 10 -X POST -H "Content-Type: application/json" -d "{\"tunnelUrl\": \"$TUNNEL_URL\"}" https://habit-snowball.zeabur.app/api/ollama-tunnel)
    echo "Sync response: $SYNC_RES"

    # 7. 持續監控背景服務是否存活，如有任一服務掛掉則以 exit 1 退出，供 launchd 自動重啟
    echo "Monitoring background services..."
    while true; do
        if ! lsof -i :11435 >/dev/null 2>&1; then
            echo "Error: Python CORS proxy died."
            exit 1
        fi
        if ! pgrep -f "cloudflared tunnel" > /dev/null; then
            echo "Error: Cloudflare Tunnel died."
            exit 1
        fi
        sleep 10
    done
else
    echo "Error: Failed to obtain Cloudflare Tunnel URL within 30 seconds."
    exit 1
fi
