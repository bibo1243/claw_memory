---
name: calendar-management
description: Google 行事曆管理原則與自動化規則。當需要新增、查詢、管理行事曆時使用此技能。
---

# 行事曆管理技能

## 預設行事曆

| 用途 | 行事曆 | Calendar ID |
|------|--------|-------------|
| 查詢 | 冠葦行程 + 慈馨 + 慈光 | bibo1243@gmail.com, tch3300@gmail.com, 1383fae5b7204ef46d5fd09f338244740bff7449da5f137ea9fdb9a9f0a1d4de@group.calendar.google.com |
| 新增 | 冠葦行程 | bibo1243@gmail.com |

## 自動新增規則

1. **對話截圖已確認時間** → 直接新增，不用問
2. **日期不清楚** → 先確認再新增
3. **預設提醒** → 活動前 **2 小時**

## 新增行程 API 範例

```bash
curl -X POST "https://www.googleapis.com/calendar/v3/calendars/bibo1243%40gmail.com/events" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "活動名稱",
    "start": {
      "dateTime": "2026-02-04T10:00:00+08:00",
      "timeZone": "Asia/Taipei"
    },
    "end": {
      "dateTime": "2026-02-04T11:00:00+08:00",
      "timeZone": "Asia/Taipei"
    },
    "reminders": {
      "useDefault": false,
      "overrides": [
        {"method": "popup", "minutes": 120}
      ]
    }
  }'
```

## 行事曆管理原則

### 1. 查詢原則
- 查詢時同時查 **冠葦行程**、**慈馨**、**慈光暨附設機構**
- **同時查詢假表**：回報行程時，務必同時執行 `vacation-schedule` 查詢當日休假狀態（上班/休假/公出），並標註在行程旁。
- 結果合併顯示，標註來源行事曆
- 格式：日期（星期）+ 時間 + 活動名稱 + [假表狀態]

### 2. 新增原則
- **自動檢查假表**：新增行程前，必須先查詢該日假表。
  - 若當天是「休假 (◎/〇/●)」，需主動提醒 Gary：「這天是休假日，確定要排行程嗎？」
  - 若當天是「上班」，則直接新增。
- **對話截圖已確認時間** → 直接新增，不用問
- **日期不清楚** → 先確認再新增
- **預設提醒** → 活動前 **2 小時**

| 使用者說 | 解讀為 |
|----------|--------|
| 明天 | +1 天 |
| 後天 | +2 天 |
| 下週X | 下一個星期X |
| X/X | 當年度該日期 |
| 中午 | 12:00 |
| 下午 | 14:00（若未指定時間）|
| 晚上 | 19:00（若未指定時間）|

## 持續更新

新的原則請加在這裡：

- （待補充）
