#!/bin/bash

# 切換到家目錄
cd ~

# 1. 確保先關閉舊的 cloudflared 隧道
pkill -f "cloudflared tunnel" || true

# 2. 清理舊的 log 檔案
rm -f ~/tunnel.log

# 3. 確保 Python CORS 代理程式正在執行 (監聽 Port 11436)
if ! lsof -i :11436 >/dev/null 2>&1; then
    echo "Starting Python CORS proxy..."
    nohup python3 ~/ollama_cors_proxy.py 11436 > ~/ollama_proxy.log 2>&1 &
    sleep 2
fi

# 4. 啟動 Cloudflare 隧道指向 Python 代理 (11436) 並強制作為 http2 (TCP) 傳輸協議以提升連線穩定度
echo "Starting Cloudflare Tunnel..."
nohup ~/cloudflared tunnel --protocol http2 --url http://127.0.0.1:11436 > ~/tunnel.log 2>&1 &

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

    # 7. 持續監控背景服務是否存活與健康
    echo "Waiting 60 seconds for DNS propagation..."
    sleep 60
    echo "Monitoring background services and tunnel health..."
    FAIL_COUNT=0
    while true; do
        # 檢查 Python CORS 代理是否存活
        if ! lsof -i :11436 >/dev/null 2>&1; then
            echo "Error: Python CORS proxy died."
            exit 1
        fi
        
        # 檢查 cloudflared 進程是否存活
        if ! pgrep -f "cloudflared tunnel" > /dev/null; then
            echo "Error: Cloudflare Tunnel process died."
            exit 1
        fi
        
        # 測試隧道網址是否健康 (curl 超時 10 秒)
        # 本地 AI 健康檢查回應應該包含 "Ollama"
        if ! curl -s --max-time 10 "$TUNNEL_URL" | grep -q "Ollama"; then
            let FAIL_COUNT=FAIL_COUNT+1
            echo "Warning: Tunnel health check failed ($FAIL_COUNT/5)."
            if [ $FAIL_COUNT -ge 5 ]; then
                echo "Error: Tunnel connection failed 5 consecutive times. Exiting to restart."
                exit 1
            fi
        else
            FAIL_COUNT=0
        fi
        
        sleep 30
    done
else
    echo "Error: Failed to obtain Cloudflare Tunnel URL within 30 seconds."
    exit 1
fi
