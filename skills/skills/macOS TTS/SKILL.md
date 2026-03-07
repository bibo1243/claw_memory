---
name: macos-tts
description: Native macOS Text-to-Speech using `say` command with ffmpeg conversion for compatibility.
metadata:
  {
    "openclaw":
      {
        "emoji": "🗣️",
        "os": ["darwin"],
        "requires": { "bins": ["say", "ffmpeg"] }
      }
  }
---

# macOS TTS

Generate speech from text using the built-in macOS `say` command, then convert to MP3 for cross-platform compatibility (e.g. sending via Telegram).

## Usage

**1. Basic Command:**

```bash
say -v "Meijia" -o temp_audio.aiff "你好，這是測試語音。"
```

*   `-v "Meijia"`: Specifies the Traditional Chinese (Taiwan) voice.
*   `-o temp_audio.aiff`: Outputs to an AIFF file (macOS native format).

**2. Convert to MP3 (Required for Telegram/Web):**

```bash
ffmpeg -i temp_audio.aiff -codec:a libmp3lame -qscale:a 2 output_audio.mp3
```

*   `ffmpeg`: Converts the audio.
*   `-codec:a libmp3lame`: Uses the MP3 encoder.
*   `-qscale:a 2`: Sets high quality (VBR).

**3. Clean up:**

```bash
rm temp_audio.aiff
```