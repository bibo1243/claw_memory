---
name: Vite Nohup Background Execution
description: 解決利用 nohup 在背景啟動 Vite 前端伺服器時，因為等待終端機輸入導致系統強制暫停連線 (Suspended) 造成 ERR_CONNECTION_REFUSED 的正確啟動策略。
---

# Vite Nohup Background Execution

## 核心問題 (The Core Problem)

當你在 Mac 或 Linux 環境使用類似以下的指令，打算將 Vite (或任何要求終端機互動的 Node 程式) 丟到背景執行時：

```bash
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

你會發現伺服器狀態看起來有在跑 (存在 PID)，但瀏覽器開啟網頁時會直接出現 `ERR_CONNECTION_REFUSED` 拒絕連線的錯誤。

這並非是伺服器當機，而是因為 **Vite Dev Server 啟動時會主動嘗試讀取終端機的鍵盤輸入 (`stdin`)** (例如：`press h + enter to show help`)。
由於被放到了背景(`&`) 且截斷了標準輸入/輸出，作業系統 (OS) 為了防範背景程式無止盡等待輸入操作，會觸發 **SIGTTIN** 信號。該信號會直接把這個程式「凍結/暫停 (Suspended)」。
結果就是：伺服器完全被卡死，任何進入的網路請求都不會被處理。

## 解法與底層邏輯 (The Solution & Underlying Logic)

要解決這個問題，必須要「主動餵給程式一個無效的空輸入源」，來欺騙或終止它等待實體終端機輸入的行為。

在 UNIX 系統中，可以使用 **`< /dev/zero`** 或 **`< /dev/null`** 來導向標準輸入。如果使用 `/dev/zero`，程式讀到的會是一連串空字元 (NULL)，能有效防止被暫停。

因此，啟動 Vite 或其他需要背景運行的前端伺服器時，最穩定的腳本配置為：

```bash
nohup npm run dev -- --host < /dev/zero > /tmp/frontend.log 2>&1 &
```

### 參數解構

1. `nohup`: 讓程式免疫 HUP 信號，當使用者登出或關閉終端時程式不會被終止。
2. `npm run dev`: 執行 Vite 開發伺服器。
3. `-- --host`: 允許外部連線 (綁定 0.0.0.0 而非 localhost/127.0.0.1，針對有時 IPv6 / IPv4 衝突的問題非常有幫助)。
4. `< /dev/zero`: 將 `/dev/zero` 導向標準輸入 (`stdin`)，避免 OS 觸發 SIGTTIN 暫停程式。 (也可以試試 `< /dev/null`)
5. `> /tmp/frontend.log`: 將標準輸出 (`stdout`) 導向檔案。
6. `2>&1`: 將標準錯誤 (`stderr`) 合併導向標準輸出。
7. `&`: 最尾端的 ampersand 代表放到背景執行。

## 檢查被 Suspended 程式的技巧

如果你想確認某個背景程式是不是被卡死了，除了用 `lsof -i :5173` 找它外，你可以使用：

```bash
ps -o pid,stat,command -p <PID>
```

觀察輸出中的 `STAT` 欄位：
- 如果看到 `T` (例如 `TN` 或 `T+`), 就代表該程式被 **Stopped (Suspended)** 了。這正是發生 `ERR_CONNECTION_REFUSED` 的元凶。
- 健康的背景服務應該是 `S` (Sleeping on an interruptible wait) 或是直接在處理時變成 `R` (Runnable)。

## 延伸慣例

未來撰寫任何 **Agent 自動化腳本 (.agent/workflows)**、常駐服務時，只要是用到 `npm run start`, `npm run dev`, `vite`, `webpack-dev-server`，且要在背景執行，請務必養成加上 `< /dev/zero` 或 `< /dev/null` 的保命習慣！
