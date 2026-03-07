---
name: image-gen
description: 生成 AI 圖片並自動上傳到圖床，可直接分享到 LINE 等通訊軟體。支援中英文提示詞。使用時機：當使用者要求生成圖片、畫圖、製作插圖時。
---

# AI 圖片生成技能

## 功能
- 使用 Google Gemini (Nano Banana Pro) 生成高品質圖片
- 自動上傳到 Catbox 圖床取得公開網址
- 可直接傳送到 LINE、Telegram 等通訊軟體

## 環境需求
- `GEMINI_API_KEY` 環境變數

## 使用方式

### 生成圖片
```bash
# 1. 生成圖片
GEMINI_API_KEY=$GEMINI_API_KEY python3 {workspace}/skills/gemini-image-simple/scripts/generate.py "提示詞" output.jpg

# 2. 上傳到圖床
curl -s --max-time 15 -F "reqtype=fileupload" -F "fileToUpload=@output.jpg" https://catbox.moe/user/api.php
```

### 一鍵腳本
```bash
{workspace}/skills/image-gen/scripts/generate-and-upload.sh "提示詞"
```

## 提示詞技巧

**風格關鍵字：**
- 寫實：`photorealistic, natural lighting, 8k`
- 插畫：`illustration, digital art, vibrant colors`
- 動漫：`anime style, studio ghibli`
- 油畫：`oil painting, impressionist style`

**構圖關鍵字：**
- `full body shot` - 全身
- `portrait` - 肖像/半身
- `close-up` - 特寫
- `wide angle` - 廣角

## 範例

| 使用者說 | 提示詞 |
|---------|--------|
| 生成一隻貓 | A cute cat sitting, photorealistic, soft lighting |
| 畫一個日落 | Beautiful sunset over ocean, vibrant orange and purple sky, photorealistic |
| 一碗拉麵 | A bowl of Japanese ramen, steam rising, top-down view, food photography |

## 傳送到 LINE

用 message 工具傳送圖片 URL：
```
message send --channel line --target <userId> --media <圖床URL>
```
