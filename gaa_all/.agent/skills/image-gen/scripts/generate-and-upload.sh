#!/bin/bash
# generate-and-upload.sh - 生成圖片並上傳到圖床
# 用法: ./generate-and-upload.sh "提示詞" [輸出檔名]

set -e

PROMPT="$1"
OUTPUT="${2:-generated_$(date +%s).jpg}"
WORKSPACE="$(dirname "$(dirname "$(realpath "$0")")")/.."

if [ -z "$PROMPT" ]; then
    echo "用法: $0 \"提示詞\" [輸出檔名]"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "錯誤: 請設定 GEMINI_API_KEY 環境變數"
    exit 1
fi

echo "🎨 生成圖片中..."
python3 "$WORKSPACE/gemini-image-simple/scripts/generate.py" "$PROMPT" "$OUTPUT"

if [ ! -f "$OUTPUT" ]; then
    echo "錯誤: 圖片生成失敗"
    exit 1
fi

echo "📤 上傳到圖床..."
URL=$(curl -s --max-time 30 -F "reqtype=fileupload" -F "fileToUpload=@$OUTPUT" https://catbox.moe/user/api.php)

if [[ "$URL" == https://* ]]; then
    echo "✅ 成功！"
    echo "📎 網址: $URL"
    echo "$URL"
else
    echo "❌ 上傳失敗: $URL"
    exit 1
fi
