---
name: gemini-image-simple
version: 1.1.0
description: 使用純 Python 標準庫透過 Gemini API 生成和編輯圖片。零依賴——適用於無法使用 pip/uv 的受限環境。
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      env: ["GEMINI_API_KEY"]
---

# Gemini Image Simple

使用 Google 的 **Nano Banana Pro** (Gemini 3 Pro Image) 生成和編輯圖片——這是最高品質的圖片生成模型。

## 為何選擇此技能

| 功能 | 此技能 | 其他 (nano-banana-pro 等) |
|---|---|---|
| **相依性** | 無 (僅標準庫) | google-genai, pillow 等 |
| **需要 pip/uv** | ❌ 否 | ✅ 是 |
| **適用於 Fly.io 免費版** | ✅ 是 | ❌ 失敗 |
| **適用於容器** | ✅ 是 | ❌ 常失敗 |
| **圖片生成** | ✅ 完整 | ✅ 完整 |
| **圖片編輯** | ✅ 是 | ✅ 是 |
| **設定複雜度** | 僅需設定 API Key | 需先安裝套件 |

**結論：** 此技能可在任何有 Python 3 的地方運作。無需套件管理器、虛擬環境或權限問題。

## 快速開始

```bash
# 生成
python3 /data/clawd/skills/gemini-image-simple/scripts/generate.py "一隻戴著小帽子的貓" cat.png

# 編輯現有圖片
python3 /data/clawd/skills/gemini-image-simple/scripts/generate.py "變成日落光線" edited.png --input original.png
```

## 用法

### 生成新圖片

```bash
python3 {baseDir}/scripts/generate.py "你的提示詞" output.png
```

### 編輯現有圖片

```bash
python3 {baseDir}/scripts/generate.py "編輯指令" output.png --input source.png
```

支援的輸入格式：PNG, JPG, JPEG, GIF, WEBP

## 環境設定

設定 `GEMINI_API_KEY` 環境變數。請至 https://aistudio.google.com/apikey 取得。

## 運作原理

使用 **Nano Banana Pro** (`nano-banana-pro-preview`) - Google 最高品質的圖片生成模型：
- 純 `urllib.request` 處理 HTTP (無需 requests 庫)
- 純 `json` 解析 (標準庫)
- 純 `base64` 編碼 (標準庫)

就這樣。無外部套件。適用於任何 Python 3.10+ 安裝。

## 模型

目前使用：`nano-banana-pro-preview` (也稱為 Gemini 3 Pro Image)

其他可用模型 (如需更改可在 generate.py 中修改)：
- `gemini-3-pro-image-preview` - 同 Nano Banana Pro
- `imagen-4.0-ultra-generate-001` - Imagen 4.0 Ultra
- `imagen-4.0-generate-001` - Imagen 4.0
- `gemini-2.5-flash-image` - Gemini 2.5 Flash 具備圖片生成功能

## 範例

```bash
# 風景
python3 {baseDir}/scripts/generate.py "日出時的霧中山脈，如照片般逼真" mountains.png

# 產品照
python3 {baseDir}/scripts/generate.py "極簡風格的咖啡杯產品照，白色背景" coffee.png

# 編輯：改變風格
python3 {baseDir}/scripts/generate.py "轉換為水彩畫風格" watercolor.png --input photo.jpg

# 編輯：增加元素
python3 {baseDir}/scripts/generate.py "在天空中加一道彩虹" rainbow.png --input landscape.png
```
