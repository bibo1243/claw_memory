# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## Things 3 CLI (Macbook Air) - ⚠️ On-Demand Only

**Status (2026-02-26)**: 預設停用寫入。僅在 Gary 明確指令時才執行。保留此區塊作為操作記憶。

- **讀取超時問題**：Things 3 CLI 讀取有時會超時（尤其任務量大時）
- **備用方案**：讀取改用 AppleScript 或 Things URL scheme 查詢
- **寫入**：繼續用 `things:///add` URL scheme（穩定）
- **負責方**：由 Macbook Air bot 執行

---

Add whatever helps you do your job. This is your cheat sheet.
