---
name: Meeting Minutes Generator
description: 從逐字稿（PDF）與議程（DOCX）等來源，產出符合正式公文格式的 Word 會議紀錄。使用 Word 內建自動大綱多層次清單編號（壹→一→（一）→1.→(1)），並搭配標楷體、緊湊行距等中文公文慣例。
---

# Meeting Minutes Generator

## 用途

從多種來源資料（逐字稿 PDF、議程 DOCX、附件等），綜合整理產出正式的 Word 會議紀錄。

## 來源資料處理原則

| 資料類型 | 說明 | 文字可信度 |
|---------|------|----------|
| 議程文件（DOCX） | 作為會議紀錄的主軸架構 | ✅ 文字正確 |
| 逐字錄音稿（PDF） | 語音辨識產出，包含實際討論內容 | ⚠️ 文字可能有誤（需根據語境判斷修正） |
| 附件（DOCX/PDF） | 議程相關的補充文件 | ✅ 文字正確 |

### 逐字稿處理注意事項
- 語音辨識常見的同音字錯誤需根據上下文修正
- 語者標記（語者1、語者2...）需根據說話內容與角色判斷對應人物
- 口語化表達需整理為正式書面語
- 重複、語助詞、不完整句子需精簡

## Word 文件格式規範

### 字型與基本設定
- **字型**：標楷體（所有文字，含大綱編號）
- **字型大小**：內文 12pt
- **行距**：1.15 倍（緊湊）
- **頁面邊距**：上下左右各 2.54cm

### 自動大綱編號系統（Multilevel List）

**必須使用 Word 內建的自動大綱編號**，不可手動打字編號。

五層架構：

```
壹、  ← Level 0: ideographLegalTraditional, 15pt, 粗體
  一、  ← Level 1: taiwaneseCounting, 13pt, 粗體
    （一）  ← Level 2: taiwaneseCounting + 括號, 12pt
      1.  ← Level 3: decimal, 12pt
        (1)  ← Level 4: decimal + 括號, 12pt
```

### 關鍵 XML 設定

```xml
<!-- 後置字元設為「不標示」，避免編號後出現多餘 Tab -->
<w:suff w:val="nothing"/>
```

每層的縮排（twips）：
| Level | left | hanging |
|-------|------|---------|
| 0 | 720 | 480 |
| 1 | 1200 | 480 |
| 2 | 1680 | 480 |
| 3 | 2160 | 360 |
| 4 | 2640 | 360 |

### 會議資訊區格式
- **不使用表格**，使用純文字段落
- **不使用 Tab 對齊**，冒號後直接接內容（無間距）
- Label 粗體，Value 一般
- 段落間距為 0

格式範例：
```
日　期：115年02月26日（四）
時　間：上午9:00-12:00
地　點：基金會會議室
主　席：詹前柏常務董事
出　席：吳碧霞董事長、廖慧雯主任、李冠葦總幹事
紀　錄：李冠葦總幹事
```

## 技術實作要點

### 使用 python-docx

```bash
pip3 install python-docx
```

### 建立自動大綱編號的核心步驟

1. **取得 numbering part**：
```python
numbering_part = doc.part.numbering_part
numbering_elm = numbering_part._element
```

2. **建立 abstractNum XML**（定義五層編號格式）：
   - 每層設定 `numFmt`、`lvlText`、`suff`、`pPr`（縮排）、`rPr`（字型）
   - `<w:suff w:val="nothing"/>` 必須加在每一層

3. **建立 num 引用**：將 `numId` 指向 `abstractNumId`

4. **段落套用編號**：透過 `w:numPr` 設定 `w:ilvl`（層級）和 `w:numId`

5. **重設子層級編號**：當換到新的（一）或（二）時，Level 3 的 `1.` 要從 1 重新開始
   - 建立新的 `w:num`，使用 `w:lvlOverride` + `w:startOverride`

### 重設編號的實作

```python
def reset_numbering_at_level(level):
    """在切換段落時，重設某層級編號從 1 開始"""
    global num_id
    max_nums = numbering_elm.findall(qn('w:num'))
    new_num_id = max([int(n.get(qn('w:numId'))) for n in max_nums], default=0) + 1
    
    override_xml = f'<w:num w:numId="{new_num_id}" {nsdecls("w")}>'
    override_xml += f'<w:abstractNumId w:val="{abstract_num_id}"/>'
    override_xml += f'<w:lvlOverride w:ilvl="{level}">'
    override_xml += '<w:startOverride w:val="1"/>'
    override_xml += '</w:lvlOverride>'
    override_xml += '</w:num>'
    
    num_element = parse_xml(override_xml)
    numbering_elm.append(num_element)
    num_id = new_num_id
```

### 使用時機
- 每次進入新的（一）、（二）等段落時，呼叫 `reset_numbering_at_level(3)` 讓 `1.` 從頭開始
- 同理，進入新的 `一、` 時如需重設（一）也可呼叫 `reset_numbering_at_level(2)`

## 會議紀錄標準結構

```
壹、追蹤事項
  一、上次會議事項追蹤
    （一）議題名稱
      1. 內容
      2. 內容
    （二）議題名稱
      1. 內容

貳、報告及討論事項
  一、議題名稱（附件X）
    （一）提案說明
    （二）討論重點
    （三）決議

參、行政管理事項
  ...

肆、其他事項
  ...

伍、待辦事項
  （表格形式：項次、待辦事項、負責人、期限）

陸、散會
```

## 待辦事項表格格式
- 使用 `Table Grid` 樣式
- 四欄：項次（1.5cm, 置中）、待辦事項（10cm）、負責人（2.5cm）、期限（3cm）
- 標題列粗體、置中
- 字型 11pt 標楷體

## 踩坑記錄

| 問題 | 原因 | 解法 |
|------|------|------|
| 編號後出現大段 Tab 空白 | Word 預設後置字元為 Tab | 加入 `<w:suff w:val="nothing"/>` |
| 每個（一）下的 1. 不從頭開始 | 同一個 numId 的計數器會持續累加 | 使用 `lvlOverride` + `startOverride` 建立新 numId |
| 會議資訊表格太醜（框線+大間距） | 使用 Table Grid 表格 | 改用純文字段落，冒號後直接接內容 |
| 行距太寬 | 預設 1.5 倍行距 | 改為 1.15 倍（w:line=276） |
| 字型未套用到東亞字元 | python-docx 的 font.name 只設定 ASCII | 需額外設定 `rFonts.set(qn('w:eastAsia'), '標楷體')` |
| 舊版 `.doc` 做文字替換後，字型與大綱符號消失 | 使用 `textutil` 或 `rtf/txt` 轉換流程時，段落/清單格式資訊可能被扁平化 | 修改 `.doc` 時優先用 Word App 內建尋找取代；禁止先轉 `txt/rtf` 再轉回 |
| `.docx` 轉存 `.doc` 後清單層級異常或段落合併 | 不同格式引擎對清單與段落控制碼相容性差 | 最終交付優先 `.docx`；若使用者堅持 `.doc`，先留 `.docx` 主檔並另存 `.doc` 副本供比對 |

## 既有 `.doc` 修改 SOP（重要）

1. 先備份原檔（例如 `xxx.pre_edit_backup.doc`）。
2. 只做「Word 內建尋找/取代」的最小變更，不走 `txt/rtf` 中介。
3. 變更後立即人工檢查三件事：
   - 自動大綱是否仍可升降層級（不是手打字串）
   - 內文與編號字型是否仍為標楷體
   - 段落是否被意外合併
4. 如檢查失敗：以 `.docx` 依本 skill 重建正確格式，並同時保留原始備份檔供回復。
5. 回報使用者時，需明確標註：
   - 哪一份是「可編輯主檔」（建議 `.docx`）
   - 哪一份是「相容副本」（`.doc`）

## 參考腳本位置

完整產出腳本範例：`/tmp/gen_meeting_minutes_v2.py`
（注意：/tmp 下的檔案可能被清除，此處僅做參考記錄）
