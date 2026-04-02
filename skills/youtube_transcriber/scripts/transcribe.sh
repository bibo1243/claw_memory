#!/bin/bash
# YouTube Transcriber - 無字幕影片轉錄與摘要
# 用法: bash transcribe.sh "https://www.youtube.com/watch?v=VIDEO_ID" [whisper_model] [language]

set -e

URL="$1"
MODEL="${2:-medium}"
LANG="${3:-zh}"
TMPDIR="/tmp/yt_transcribe"

if [ -z "$URL" ]; then
    echo "❌ 用法: bash transcribe.sh \"YOUTUBE_URL\" [model] [language]"
    echo "   model: tiny|base|small|medium|large (預設: medium)"
    echo "   language: zh|en|ja|... (預設: zh)"
    exit 1
fi

mkdir -p "$TMPDIR"

echo "📥 Step 1/3: 下載音訊..."
yt-dlp -x --audio-format mp3 \
    -o "$TMPDIR/audio.%(ext)s" \
    --no-playlist \
    --quiet \
    "$URL"

AUDIO_FILE="$TMPDIR/audio.mp3"
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ 音訊下載失敗"
    exit 1
fi
echo "✅ 音訊下載完成: $AUDIO_FILE"

echo ""
echo "🎤 Step 2/3: Whisper 語音轉文字 (模型: $MODEL, 語言: $LANG)..."
whisper "$AUDIO_FILE" \
    --model "$MODEL" \
    --language "$LANG" \
    --output_dir "$TMPDIR" \
    --output_format txt \
    --verbose False

TRANSCRIPT="$TMPDIR/audio.txt"
if [ ! -f "$TRANSCRIPT" ]; then
    echo "❌ 轉錄失敗"
    exit 1
fi

CHAR_COUNT=$(wc -c < "$TRANSCRIPT")
echo "✅ 轉錄完成: $TRANSCRIPT ($CHAR_COUNT 字元)"

echo ""
echo "📝 Step 3/3: 摘要中..."
echo ""
echo "========== 逐字稿 =========="
cat "$TRANSCRIPT"
echo ""
echo "========== 逐字稿結束 =========="
echo ""

# 如果有 summarize CLI 且有 GEMINI_API_KEY，自動摘要
if command -v summarize &> /dev/null && [ -n "$GEMINI_API_KEY" ]; then
    echo "🤖 AI 摘要："
    echo ""
    summarize "$TRANSCRIPT" --length long
else
    echo "ℹ️  逐字稿已輸出。若要 AI 摘要，請安裝 summarize CLI 並設定 GEMINI_API_KEY。"
fi

echo ""
echo "📁 檔案位置:"
echo "   音訊: $AUDIO_FILE"
echo "   逐字稿: $TRANSCRIPT"
