---
name: text-to-speech
description: 將文字轉換為語音檔案 (MP3) 並回傳路徑。使用 OpenAI API。
---

# Text to Speech (TTS)

此技能使用 OpenAI 的 TTS API 將文字轉換為自然的語音。

## 成功經驗 (2026-02-20)
- **問題**：早期測試中，音訊編碼不相容，導致部分平台（如 Telegram/LINE）無法播放，或只唸出開頭名字（截斷）。
- **解決方案**：
    1.  使用 OpenAI `tts-1` 模型生成語音。
    2.  強制輸出為標準 `mp3` 格式。
    3.  確保 `stream_to_file` 正確寫入二進位流。
- **驗證**：Gary 確認音訊清晰，且內容與文字完全一致。

## 功能

- **轉換 (Convert)**: 輸入文字，輸出 MP3 檔案路徑。

## 依賴

- `openai` python package
- `OPENAI_API_KEY` 環境變數

## 腳本

- `scripts/tts.py`: 執行轉換的主程式。
