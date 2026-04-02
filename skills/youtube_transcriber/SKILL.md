---
name: YouTube Transcriber
description: 使用 yt-dlp + Whisper 轉錄沒有字幕的 YouTube 影片，再透過 Summarize CLI 進行摘要。適用於任何語言的影片。
---

# YouTube Transcriber（無字幕影片轉錄與摘要）

> 當 Summarize CLI 無法取得 YouTube 字幕時，使用此 Skill 作為備援方案。

## 流程

```
YouTube URL → yt-dlp 下載音訊 → Whisper 語音轉文字 → Summarize 摘要
```

## 使用方式

### 完整流程（一鍵腳本）

```bash
bash {baseDir}/scripts/transcribe.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 手動分步執行

#### Step 1: 下載音訊
```bash
yt-dlp -x --audio-format mp3 -o "/tmp/yt_audio.%(ext)s" "YOUTUBE_URL"
```

#### Step 2: Whisper 轉錄
```bash
whisper "/tmp/yt_audio.mp3" --model medium --language zh --output_dir /tmp --output_format txt
```

**模型選擇：**
| 模型 | 速度 | 準確度 | 適用場景 |
|------|------|--------|---------|
| `tiny` | ⚡ 最快 | 一般 | 快速預覽 |
| `base` | 快 | 尚可 | 英文為主 |
| `small` | 中等 | 好 | 一般用途 |
| `medium` | 較慢 | 很好 | 中文推薦 |
| `large` | 最慢 | 最佳 | 需要最高準確度 |

#### Step 3: 摘要
```bash
summarize "/tmp/yt_audio.txt" --length long
```

## 前置需求

- `yt-dlp`（brew install yt-dlp）
- `whisper`（brew install openai-whisper）
- `summarize`（brew install steipete/tap/summarize）
- `GEMINI_API_KEY` 環境變數（供 Summarize 使用）

## 注意事項

- Whisper `medium` 模型對中文效果最好，首次使用會自動下載模型（約 1.5GB）
- 音訊檔案暫存在 `/tmp/`，用完後可刪除
- 長影片（>1小時）建議用 `small` 模型加速
