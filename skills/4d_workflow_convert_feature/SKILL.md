---
name: 4D Workflow GCal ↔ Notion 互轉功能
description: 記錄 4D Workflow 中 GCal 與 Notion 雙向搬移互轉功能的完整實作架構、前後端協作模式、常見坑點與除錯 SOP。
---

# 4D Workflow GCal ↔ Notion 互轉功能

## 1. 功能概述

在 Timeline（今日行程）的任何卡片上，hover 後右上角出現 **⟳ 轉換圖示**，點擊後可完成**搬移式互轉**（原始資料刪除）：

| 來源卡片 | 圖示顏色 | 轉換後 | 原始資料 |
|----------|----------|--------|---------|
| Google 行事曆事件 (GCal) | 紫色 ⟳ | Notion 任務（Tasks DB） | **GCal 事件刪除** |
| Notion 任務 | 藍色 ⟳ | GCal 事件（冠葦行程） | **Notion 任務封存** |

---

## 2. 前端架構

### 2-a. `TimelineBlock` 元件（`Timeline.tsx`）

```tsx
// Props 新增
onConvert?: (task: Task) => Promise<void>;

// 按鈕 UI（hover 才顯示，點擊後旋轉動畫）
const [converting, setConverting] = useState(false);

{onConvert && (
  <div
    className="opacity-0 group-hover:opacity-100 transition-opacity"
    onPointerDown={(e) => e.stopPropagation()}  // ← 阻止觸發拖曳
    onClick={async (e) => {
      e.stopPropagation();
      if (converting) return;
      setConverting(true);
      await onConvert(task);
      setConverting(false);
    }}
  >
    <RefreshCw
      size={isCompact ? 11 : 13}
      className={`${isGcal ? 'text-purple-300' : 'text-blue-300'} ${converting ? 'animate-spin' : ''}`}
    />
  </div>
)}
```

> ⚠️ **必須在 `onPointerDown` 中呼叫 `e.stopPropagation()`**，否則 dnd-kit 的拖曳監聽器會攔截點擊事件，導致按鈕完全沒有反應。

### 2-b. `Timeline` 主元件

```tsx
// TimelineProps 中加入
onConvertTask?: (task: Task) => Promise<void>;

// 傳入 TimelineBlock
<TimelineBlock onConvert={onConvertTask} ... />
```

### 2-c. `useSync.ts` — `convertTask` 函數

```typescript
const convertTask = useCallback(async (task, direction) => {
  const payload = {
    title: task.title,
    date: task.date,
    time: task.time,
    duration: task.duration,
    description: task.description,
  };

  if (direction === 'gcal_to_notion') {
    payload.gcalEventId = task.gcalEventId;
    payload.calendarId = task.calendarId;
  } else {
    payload.notionPageId = task.notionPageId || task.id;
  }

  const res = await fetch(`${API_BASE}/api/convert?direction=${direction}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await res.json();
  return json.success;
}, []);
```

### 2-d. `App.tsx` — `handleConvertTask`

```typescript
const handleConvertTask = useCallback(async (task: Task) => {
  const direction = task.source === 'gcal' ? 'gcal_to_notion' : 'notion_to_gcal';
  const ok = await sync.convertTask(task, direction);
  if (!ok) return;

  // 樂觀移除
  if (task.source === 'gcal') {
    sync.setGcalTasks(prev => prev.filter(t => t.id !== task.id));
  } else {
    setTasks(prev => prev.filter(t => t.id !== task.id), false);
  }

  // 1.2 秒後 re-sync 載入新資料
  setTimeout(() => sync.syncAll(), 1200);
}, [sync, setTasks]);
```

---

## 3. 後端架構（`server.ts`）

```typescript
app.post('/api/convert', async (req, res) => {
  const direction = req.query.direction; // 'gcal_to_notion' | 'notion_to_gcal'

  if (direction === 'gcal_to_notion') {
    // 1. 建立 Notion 任務（target DB: 30a1fbf9-30df-81aa-a9dc-ddb4a05f01b2）
    // 2. 刪除 GCal 事件（gcalEventId 需去除 "gcal-" 前綴）
  }

  if (direction === 'notion_to_gcal') {
    // 1. 在 primary calendar 建立 GCal 事件
    // 2. 封存 Notion 任務（notionService.deleteTask）
  }
});
```

> **GCal 事件 ID 處理**：前端傳來的 `gcalEventId` 可能帶有 `"gcal-"` 前綴（本地 ID 用途），後端需 `.replace(/^gcal-/, '')` 才能呼叫 Google API。

---

## 4. 常見問題與坑點

### 坑點 1：按鈕點擊沒有反應
- **原因**：`onPointerDown` 沒有 `stopPropagation`，dnd-kit Draggable 的 `...listeners` 在 `pointerdown` 就攔截了事件，導致 `onClick` 永遠不觸發。
- **解法**：所有互動子元素（按鈕、toggle）必須在 wrapping div 的 `onPointerDown` 加 `e.stopPropagation()`。

### 坑點 2：後端路由 404
- **原因**：後端沒有重啟（舊的 process 還在跑），新寫入的路由沒有載入。
- **診斷方式**：
  ```bash
  # 測試路由是否正確掛載
  curl -s -X POST 'http://localhost:3001/api/convert?direction=gcal_to_notion' \
    -H 'Content-Type: application/json' \
    -d '{"title":"test","date":"2026-03-06","time":"10:00","duration":1,"gcalEventId":"fake","calendarId":"primary"}'
  # 如果回傳 HTML 404（包含 <!DOCTYPE），就是路由沒載入
  # 如果回傳 JSON {"success":false,"error":"Not Found"}，是 GCal API 問題（ID 不存在），路由本身 OK
  ```
- **解法**：參見 `4d_workflow_backend_architecture` Skill 的「後端重啟 SOP」。

### 坑點 3：Vite HMR 沒有更新
- **原因**：`pkill -f vite` 有時殺不乾淨舊 process（有殭屍進程）。
- **解法**：用 port 強制殺，再重啟：
  ```bash
  lsof -ti:5173 | xargs kill -9 2>/dev/null
  sleep 1
  nohup npm run dev < /dev/zero > /tmp/frontend.log 2>&1 &
  ```

### 坑點 4：`useSync.ts` 有孤兒代碼（Orphan Code）
- **症狀**：編輯 `useCallback` 函數體後，舊的函數體殘留在檔案中，造成語法錯誤或不預期行為。
- **解法**：使用 `grep_search` 確認目標函數在檔案中的行數，`view_file` 仔細確認起訖行，再用精確的 `replace_file_content`。

---

## 5. 資料流總覽

```
使用者點擊 ⟳
     ↓
TimelineBlock.onClick → setConverting(true) → onConvert(task)
     ↓
App.handleConvertTask → sync.convertTask(task, direction)
     ↓
useSync.convertTask → POST /api/convert?direction=...
     ↓ (後端)
server.ts /api/convert
  → [gcal_to_notion] createTask(Notion) + deleteEvent(GCal)
  → [notion_to_gcal] insertEvent(GCal) + deleteTask(Notion)
     ↓ (前端，API 成功後)
樂觀移除卡片 → setTimeout 1.2s → syncAll() 重新拉資料
```

---

## 6. 相關檔案位置

| 檔案 | 功能 |
|------|------|
| `frontend/src/components/Timeline.tsx` | UI 按鈕、`TimelineBlock` |
| `frontend/src/hooks/useSync.ts` | `convertTask` 函數 |
| `frontend/src/App.tsx` | `handleConvertTask`、props 傳遞 |
| `backend/src/api/server.ts` | `/api/convert` 端點（line ~170） |
