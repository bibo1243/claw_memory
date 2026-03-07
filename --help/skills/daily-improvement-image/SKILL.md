---
name: daily-improvement-image
description: 讀取 Notion 中的「日精進」內容，使用 wkhtmltoimage (或其他工具) 生成精美圖片，並回傳給使用者。支援自動更新 Notion 頁面的 Cover 或內容圖片。
---

# 日精進圖片生成 (Daily Improvement Image)

此技能用於將 Gary 每日在 Notion 撰寫的「日精進」心得，轉化為易於分享和回顧的圖片格式。

## 流程
1. **讀取內容**: 從 Notion 資料庫 (Tasks) 讀取當日或指定的日精進內容。
2. **生成圖片**: 使用 HTML 模板 + CSS 渲染出精美排版，再轉換為 JPG/PNG。
3. **回傳與同步**: 將圖片回傳給 Gary (Telegram)，並可選擇同步回 Notion。

## 依賴
- `wkhtmltoimage` (系統層級) 或其他 Image Generation 工具
- Notion API (讀取與寫入)

## 腳本
- `scripts/notion_get_latest_diary.py`: 讀取最新日精進。
- `scripts/generate_image.sh`: 執行圖片生成 (範例)。
