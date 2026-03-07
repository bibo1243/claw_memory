---
name: shared-memory
description: 用於兩個 Bot (GaaClaw, gaa1243) 讀寫共同記憶 (gaa_all/對話.md)。每次對話前讀取，回應後寫入。
---

# 共享記憶 (Shared Memory)

此技能用於讀取和寫入 Google Drive 上的 `gaa_all/對話.md`，以實現地端 (MacBook) 和雲端 (Zeabur) 兩個 Bot 的記憶同步。

## 功能

### 1. 讀取記憶 (Read)
- 從 Google Drive 下載 `gaa_all/對話.md` 的最新內容。
- 用於對話開始前，了解另一個 Bot 說了什麼。

### 2. 寫入記憶 (Write)
- 將當前對話內容追加到 `gaa_all/對話.md`。
- 格式：`[時間] [Bot名稱] [訊息]`

## 腳本

- `read_shared.py`: 讀取最近對話 (預設最後 20 行)
- `write_shared.py`: 追加對話紀錄
