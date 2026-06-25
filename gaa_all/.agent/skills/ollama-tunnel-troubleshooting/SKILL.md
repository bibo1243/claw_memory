---
name: ollama-tunnel-troubleshooting
description: 當本地 AI/Ollama 無反應、超時、或報 CORS 錯誤時，用於排除 Cloudflare Tunnel、CORS Proxy 與 Ollama 模型名稱不符等常見地端故障。
---

# 本地 AI 與 Cloudflare Tunnel 疑難排解指南

本指南記錄了在 `habit-snowball` 專案中，如何解決本地 AI (Ollama) 連線超時、CORS 跨域阻擋、端口衝突與模型名稱不一致的實務經驗。

## 典型故障與根本原因

### 1. 點擊 AI 按鈕無任何反應
- **原因**：前端 `js/app.js` 中的非同步處理函數出現未閉合的 JavaScript 語法錯誤（例如 `try` 塊後缺少對應的 `finally` 或 `catch` 大括號），導致瀏覽器加載時解析失敗，所有 AI 按鈕的點擊事件無法掛載。

### 2. 本地 AI 請求總是超時 (Timeout)
- **原因 1：模型名稱不匹配**。例如前端硬編碼請求不存在的模型名稱（如 `gemma4:e4b`），而本地 Ollama 僅安裝了 `gemma4:e2b`，導致 Ollama 由於在本地找不到模型而嘗試拉取下載（或卡死）直到超時。
- **原因 2：Tunnel 連上了別台電腦**。多人協同或有多台測試機時，Cloudflare Tunnel 隨機分配網址被另一台電腦（例如裝有 `e4b` 的辦公室機器）同步到了雲端，導致本地瀏覽器去連線那台機器，在請求 `e2b` 時返回 404，且因超時限制是全局共享，導致後續 fallback 請求也直接被 abort。

### 3. 控制台顯示 CORS 跨來源政策阻擋 (net::ERR_FAILED 200)
- **原因**：系統背景有常駐守護進程（如 `ollama_native_proxy.py`）強佔了預設的 `11435` 端口，使得 `start_ollama_tunnel.sh` 無法成功啟動支援跨域 CORS 標頭的 `ollama_cors_proxy.py`。
- 當 11435 端口無服務監聽時，Cloudflare Tunnel 會返回其自身的錯誤頁面，此頁面沒有附帶 `Access-Control-Allow-Origin` 頭，因而被瀏覽器 CORS 政策阻擋。

---

## 核心解決方案架構

### 1. 避讓端口（改用 11436）
- 為了避免與系統常駐進程搶奪 11435 端口，我們將專案的本地 CORS Proxy 監聽端口和 Cloudflare Tunnel 統一改為 **`11436`**。
- 修改 `ollama_cors_proxy.py` 支援動態讀取端口參數：
  ```python
  if __name__ == '__main__':
      port = 11435
      if len(sys.argv) > 1:
          try: port = int(sys.argv[1])
          except ValueError: pass
      run(port)
  ```

### 2. 精準檢測端口監聽
- 修改 `start_ollama_tunnel.sh` 的進程偵測，將 `pgrep -f "ollama_cors_proxy.py"` 改為更精準的 `lsof -i :11436`，避免 `find` 或 `grep` 指令本身的關鍵字造成 Shell 腳本誤判而跳過啟動。
  ```bash
  # 確保 Python CORS 代理程式監聽 Port 11436
  if ! lsof -i :11436 >/dev/null 2>&1; then
      nohup python3 ~/ollama_cors_proxy.py 11436 > ~/ollama_proxy.log 2>&1 &
      sleep 2
  fi
  ```

### 3. 前端自適應多模型輪詢與超時隔離
- 在 `js/app.js` 的 `callGoogleAiJson` 中，依序嘗試本地常見模型：`['gemma4:e2b', 'gemma4:e4b']`。
- **超時隔離**：為每一次模型 fetch 使用獨立的 `AbortController` 與 `setTimeout`（每個模型各自擁有完整的 20 秒生成超時空間），如果得到 404 (Model not found)，則在 1 秒內無縫嘗試下一順位模型，以最大程度相容多台電腦的模型差異。

---

## 日常運維與排錯步驟

當發現網頁的 AI 按鈕再次顯示 `已使用本地規則` 或連線紅燈時，請依序執行以下步驟：

### Step 1: 檢查本地進程狀態
```bash
# 檢查 cloudflared 與 ollama 代理進程是否正常運行
ps aux | grep -E "cloudflared|ollama"
```

### Step 2: 檢查 11436 端口監聽
```bash
# 確認 Python CORS 代理是否正常在 11436 端口監聽
lsof -i :11436
```

### Step 3: 重啟本地 Tunnel 服務
如果服務中斷，可以手動在 terminal 重啟：
```bash
# 1. 殺死舊的隧道
pkill -f "cloudflared tunnel"
pkill -f "start_ollama_tunnel.sh"

# 2. 啟動並重新同步 URL
bash ~/個人app/habit-snowball/start_ollama_tunnel.sh
```
啟動成功後，日誌應顯示：
`Success! Tunnel URL is: https://xxxx.trycloudflare.com`
`Sync response: {"ok":true,...}`
此時重新整理網頁即可恢復暢通。
