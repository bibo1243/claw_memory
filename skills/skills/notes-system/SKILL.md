---
name: notes-system
description: 備忘錄與參考資料管理系統。用於新增、查詢、搜尋備忘錄。當使用者說「記下來」「備忘」「筆記」「記錄這個」「查詢備忘錄」「找之前記的」時使用此技能。支援分類檢索：產品、食譜、工作、健康、財務、聯絡人、其他。
---

# 備忘錄系統

## 資料結構

所有備忘錄存放在 `/home/node/.openclaw/workspace/notes/` 目錄下。

### 檔案格式

每則備忘錄以 YAML frontmatter + Markdown 內容儲存：

```markdown
---
title: 標題
category: 分類
tags: [標籤1, 標籤2]
created: 2026-02-07
updated: 2026-02-07
---

內容...
```

### 分類 (category)

- `product` - 產品資訊（如精油、保健品、電器說明）
- `recipe` - 食譜、料理筆記
- `work` - 工作相關備忘
- `health` - 健康、醫療資訊
- `finance` - 財務、帳務記錄
- `contact` - 聯絡人資訊
- `reference` - 參考資料
- `other` - 其他

### 檔名規則

`YYYYMMDD-簡短標題.md`，例如：`20260207-貴格精油.md`

## 操作指令

### 新增備忘錄

使用 `scripts/notes.py add` 或直接建立檔案：

```bash
python3 scripts/notes.py add --title "標題" --category "product" --tags "精油,保健" --content "內容"
```

### 列出所有備忘錄

```bash
python3 scripts/notes.py list [--category 分類]
```

### 搜尋備忘錄

```bash
python3 scripts/notes.py search --query "關鍵字"
python3 scripts/notes.py search --category "product"
python3 scripts/notes.py search --tag "精油"
```

### 讀取備忘錄

```bash
python3 scripts/notes.py get --file "20260207-貴格精油.md"
```

## 使用情境

1. **記錄產品資訊**：拍照後請 Pi 記錄產品成分、用法
2. **查詢之前記錄**：「之前記的精油資料」「找產品備忘」
3. **分類瀏覽**：「列出所有產品類備忘」「健康相關的筆記有哪些」
4. **關鍵字搜尋**：「搜尋薰衣草」「找有關圍爐的備忘」

## 注意事項

- 圖片無法直接存入備忘錄，但可以記錄圖片的文字內容
- 重要資訊建議加上多個標籤方便日後檢索
