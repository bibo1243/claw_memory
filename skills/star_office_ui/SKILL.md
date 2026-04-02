---
name: Star Office UI Manager
description: 管理像素辦公室看板 (Star Office UI)，同步 Agent 狀態與昨日小記。
---

# 🏢 Star Office UI 管理指南

## 🚀 服務資訊
- **本地網址**: http://127.0.0.1:18795
- **安裝路徑**: `/Users/leegary/個人app/Star-Office-UI`
- **日誌檔案**: `/Users/leegary/個人app/Star-Office-UI/office.log`
- **自定義看板**: 已整合「Gary 假表看板」至左下角「昨日小記」區域。

## 🛠️ 常用指令

### 1. 更新 Agent 狀態
切換 Max 在辦公室中的位置與狀態：
```bash
cd /Users/leegary/個人app/Star-Office-UI
source venv/bin/activate
python3 set_state.py <state> "<message>"
```

### 2. 更新假表看板
如果假表有變動，請執行快取更新：
```bash
python3 /Users/leegary/個人app/Star-Office-UI/backend/update_leave_cache.py
```

### 3. 重啟後端服務
```bash
cd /Users/leegary/個人app/Star-Office-UI/backend
source ../venv/bin/activate
nohup python3 app.py > ../office.log 2>&1 &
```

## 📝 自動化同步規則
1. **假表整合**：昨日小記面板會自動置頂顯示今日休假狀態及未來四天的排休簡記。
2. **記憶同步**：自動從 `/Users/leegary/.openclaw/workspace/memory/` 抓取最新日誌進行脱敏展示。
