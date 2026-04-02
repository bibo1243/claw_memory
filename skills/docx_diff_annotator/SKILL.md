---
name: DOCX Diff Annotator
description: 比對兩份 Word 文件（新舊版），在不變更原始格式的前提下，以紅色標註修改處；並可從 PDF 會議逐字稿中擷取遺漏的討論要點，以綠色補充標註。產出一份帶有完整修訂標記的 DOCX 檔案。
---

# DOCX Diff Annotator（Word 文件差異比對與修訂標註）

## 用途

當使用者提供兩份版本不同的 Word 文件（一份舊、一份新），需要：
1. 找出所有修改處
2. 在**新版**文件上標註修改（紅色），同時保留舊版被取代的文字（灰色刪除線）
3. （可選）再參考 PDF 會議逐字稿，找出計畫書中未涵蓋的討論要點，以綠色補充

最終產出一份**修改標註版 DOCX**。

---

## ⚠️ 核心原則：保留原始格式

> **最重要的一條規則：絕對不要從零建立新文件，必須在既有文件上進行操作。**

這條規則的原因：
- Word 文件包含大量隱藏的格式資訊（樣式、表格合併、欄寬、邊界、頁首頁尾、甘特圖色塊等）
- 用 `python-docx` 從零 `Document()` 建檔會遺失所有這些格式
- 我們的策略是：**開啟新版文件 → 只修改需要標註的段落 → 另存新檔**

### 段落操作的鐵律

1. **只對有修改的段落進行 `para.clear()` + 重新 `add_run()`**
2. **沒有修改的段落，完全不碰**
3. **表格中的儲存格也是一樣：只清除有差異的 cell，重建其內容**
4. **新增段落用 `insert_paragraph_after()`，不要用 `doc.add_paragraph()`**（後者只會加在文件最末端）

---

## 完整 SOP（標準作業流程）

### 第一階段：提取文件內容

#### Step 1.1：提取段落文字

```python
from docx import Document

doc_old = Document('舊版.docx')
doc_new = Document('新版.docx')

# 提取所有段落的文字與樣式名稱
for i, para in enumerate(doc_old.paragraphs):
    print(f'[{i}] style={para.style.name} | {repr(para.text)}')
```

> **為什麼要 `repr()`？** 因為需要看見換行符 `\n`、空白等隱藏字元，這些在比對時很重要。

#### Step 1.2：提取表格內容

```python
for ti, table in enumerate(doc_old.tables):
    print(f'--- Table {ti} ({len(table.rows)} rows x {len(table.columns)} cols) ---')
    for ri, row in enumerate(table.rows):
        cells = [cell.text.replace('\n', '\\n') for cell in row.cells]
        print(f'  Row {ri}: {cells}')
```

> **注意**：`python-docx` 的表格如果有合併儲存格，同一個 cell 可能會在多個位置重複出現。比對時以 `cell.text` 為準。

#### Step 1.3：對兩份文件都做 Step 1.1 + 1.2

分別列印舊版和新版的所有段落與表格，留存完整的文字記錄供後續比對。

---

### 第二階段：比對差異

#### Step 2.1：段落層級 Diff

使用 Python 標準庫 `difflib.SequenceMatcher` 做段落層級的差異比對：

```python
import difflib

old_paras = [p.text for p in doc_old.paragraphs]
new_paras = [p.text for p in doc_new.paragraphs]

sm = difflib.SequenceMatcher(None, old_paras, new_paras)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != 'equal':
        print(f'\n{tag}: old[{i1}:{i2}] -> new[{j1}:{j2}]')
        if tag in ('replace', 'delete'):
            for i in range(i1, i2):
                print(f'  OLD[{i}]: {repr(old_paras[i][:100])}')
        if tag in ('replace', 'insert'):
            for j in range(j1, j2):
                print(f'  NEW[{j}]: {repr(new_paras[j][:100])}')
```

`tag` 類型說明：
| tag | 含義 | 處理方式 |
|-----|------|---------|
| `equal` | 內容完全相同 | 不處理 |
| `replace` | 舊版被新版取代 | 紅色標註新內容 + 灰色刪除線標示舊內容 |
| `insert` | 新版新增的段落 | 整段標為紅色 + 加【新增】前綴 |
| `delete` | 舊版有但新版刪除 | 通常不在新版文件標註（文件以新版為主體） |

#### Step 2.2：表格層級 Diff

逐表比對每個 cell 的文字內容：

```python
for ti in range(min(len(doc_old.tables), len(doc_new.tables))):
    t_old = doc_old.tables[ti]
    t_new = doc_new.tables[ti]
    for ri in range(min(len(t_old.rows), len(t_new.rows))):
        for ci in range(min(len(t_old.rows[ri].cells), len(t_new.rows[ri].cells))):
            old_text = t_old.rows[ri].cells[ci].text
            new_text = t_new.rows[ri].cells[ci].text
            if old_text != new_text:
                print(f'Table {ti}, Row {ri}, Col {ci}:')
                print(f'  OLD: {repr(old_text)}')
                print(f'  NEW: {repr(new_text)}')
```

#### Step 2.3：文字內 Diff（可選但推薦）

對於 `replace` 類型的段落，進一步比對新舊段落的文字，找出具體修改了哪些字：

```python
# 用人工閱讀比較新舊段落文字，找出具體差異詞句
# 例如：
# OLD: '希望透過數位化管理，保障同仁勞動權益'
# NEW: '希望透過資訊化數位化管理，降低組織行政管理的負擔保障同仁勞動權益'
# 差異：新增了「資訊化」、新增了「降低組織行政管理的負擔」
```

> **為什麼不用自動化 word-level diff？** 因為中文沒有空格分詞，自動 diff 容易產生碎片化的結果。人工閱讀找出語意差異更精確。

---

### 第三階段：在新版文件上標註修改

> ⚡ **關鍵：我們操作的是新版文件的副本，不是從零建檔。**

#### Step 3.0：前置準備 — 工具函式

```python
from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_highlight(run, color='yellow'):
    """為 run 加上螢光筆標記"""
    rPr = run._r.get_or_add_rPr()
    highlight = OxmlElement('w:highlight')
    # 可用顏色：yellow, green, cyan, magenta, red, darkYellow, blue 等
    highlight.set(qn('w:val'), color)
    rPr.append(highlight)

def add_strikethrough(run):
    """為 run 加上刪除線"""
    rPr = run._r.get_or_add_rPr()
    strike = OxmlElement('w:strike')
    strike.set(qn('w:val'), 'true')
    rPr.append(strike)

def insert_paragraph_after(paragraph, text='', style=None):
    """在指定段落之後插入新段落（不會跑到文件末尾）"""
    new_p = OxmlElement('w:p')
    paragraph._p.addnext(new_p)
    new_para = paragraph.__class__(new_p, paragraph._element.getparent())
    if style:
        new_para.style = style
    return new_para
```

#### Step 3.1：開啟新版文件

```python
doc = Document('新版.docx')
```

> **不是 `Document()`！** 必須開啟既有文件，才能保留所有原始格式。

#### Step 3.2：標註「修改」的段落（replace 類型）

對於文字有修改的段落，先 `clear()` 再重建 runs：

```python
# 範例：假設 para[4] 有修改
para = doc.paragraphs[4]
para.clear()  # 清除所有 runs，但段落本身的樣式/格式不變

# 重建：未修改的部分用普通 run
run = para.add_run('未修改的文字前半段')

# 修改的部分用紅色粗體 + 黃色螢光
r_new = para.add_run('新增或修改的文字')
r_new.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)  # 紅色
r_new.font.bold = True
add_highlight(r_new, 'yellow')

# 被取代的舊文字用灰色刪除線（讓讀者知道原來寫什麼）
r_old = para.add_run('舊版被取代的文字')
r_old.font.color.rgb = RGBColor(0x80, 0x80, 0x80)  # 灰色
add_strikethrough(r_old)

# 繼續未修改的文字
run2 = para.add_run('未修改的文字後半段')
```

> **重點**：`para.clear()` 只清除段落的 runs（文字內容），不會動到段落的 `pPr`（段落屬性：樣式、縮排、行距），所以段落格式會保留。

#### Step 3.3：標註「全新」的段落（insert 類型）

對於新版新增的整段文字：

```python
para = doc.paragraphs[5]  # 新版中新增的段落
para.clear()
r = para.add_run('【新增】這是新版新增的討論內容。')
r.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
r.font.bold = True
add_highlight(r, 'yellow')
```

#### Step 3.4：標註表格中的修改

```python
table = doc.tables[3]
cell = table.rows[5].cells[1]

# 清除 cell 中的文字（保留 cell 格式）
for p in cell.paragraphs:
    p.clear()

# 重建內容
cell.paragraphs[0].add_run('未修改的文字\n')
r_new = cell.paragraphs[0].add_run('（新增的補充說明）')
r_new.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)
r_new.font.bold = True
add_highlight(r_new, 'yellow')
```

#### Step 3.5：另存新檔

```python
doc.save('修改標註版.docx')
```

> **絕對不要覆蓋原檔！** 產出為獨立的新檔案。

---

### 第四階段：補充 PDF 會議逐字稿（綠色標註）

當使用者提供額外的 PDF 會議錄音逐字稿時，可以找出計畫書中遺漏的討論要點，以綠色標註補充。

#### Step 4.1：提取 PDF 文字

```python
import pdfplumber

with pdfplumber.open('會議逐字稿.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f'=== PAGE {i+1} ===')
        print(text)
```

> **備選方案**：如果沒有 `pdfplumber`，可用 `PyPDF2`：
> ```python
> from PyPDF2 import PdfReader
> reader = PdfReader('會議逐字稿.pdf')
> for page in reader.pages:
>     print(page.extract_text())
> ```

#### Step 4.2：閱讀 PDF 並摘要關鍵討論要點

1. **逐頁閱讀** PDF 逐字稿
2. **識別討論主題**：通常會按照計畫書的章節順序討論
3. **記錄關鍵意見**：
   - 誰說了什麼（語者識別）
   - 決策性意見（「建議...」「不需要...」「應該...」）
   - 實務問題反映（困境、風險）
   - 達成的共識

4. **與已標註的文件對照**：哪些討論要點已經在新版文件中反映，哪些是遺漏的

> **注意**：使用者可能會指定「某某會議之後的內容不要列入」，要根據 PDF 內容的語境判斷界線。通常會從討論主題的轉換（例如從人資系統轉到人事調動）來判斷。

#### Step 4.3：在標註版文件上用綠色補充

```python
# 開啟先前產出的標註版文件
doc = Document('修改標註版.docx')

# 找到要插入的位置（用文字內容定位）
target_idx = None
for i, p in enumerate(doc.paragraphs):
    if '某個關鍵文字' in p.text:
        target_idx = i
        break

# 在目標段落後方插入綠色補充
if target_idx:
    target_para = doc.paragraphs[target_idx]
    new_para = insert_paragraph_after(target_para)
    r = new_para.add_run('【會議討論-PDF】具體的討論內容摘要...')
    r.font.color.rgb = RGBColor(0x00, 0x80, 0x00)  # 綠色
    r.font.bold = True
    add_highlight(r, 'green')

# 覆寫儲存（此時是覆寫標註版，不是原始文件）
doc.save('修改標註版.docx')
```

> **定位技巧**：因為前面標註修改時可能插入了新段落，段落索引會偏移。用 `for i, p in enumerate(doc.paragraphs)` 搜尋文字內容來定位更可靠。

---

## 顏色系統規範

| 元素 | 字色 RGB | 螢光色 | 用途 |
|------|---------|--------|------|
| 新增/修改的文字 | `(0xFF, 0x00, 0x00)` 紅色 | `yellow` 黃色 | 新舊版比對的差異 |
| 全新段落前綴 | `(0xFF, 0x00, 0x00)` 紅色 | `yellow` 黃色 | 加上【新增】或【新增討論紀錄】 |
| 被取代的舊文字 | `(0x80, 0x80, 0x80)` 灰色 | 無 | 刪除線顯示原文 |
| PDF 會議補充 | `(0x00, 0x80, 0x00)` 綠色 | `green` 綠色 | 加上【會議討論-PDF】 |

---

## 踩坑記錄

| 問題 | 原因 | 解法 |
|------|------|------|
| 從零 `Document()` 建檔後格式全丟失 | python-docx 新建文件不繼承任何格式 | **必須** `Document('既有檔案.docx')` 開啟既有文件 |
| `doc.add_paragraph()` 跑到文件末尾 | python-docx 的 add_paragraph 只能追加到最後 | 使用 `insert_paragraph_after()` 在指定位置後插入 |
| `para.clear()` 後樣式消失 | 誤以為 clear 會清掉一切 | `clear()` 只清除 runs，段落的 pPr（樣式、縮排）會保留 ✅ |
| 插入新段落後索引偏移 | 每插入一個段落，後續段落的索引+1 | 第二輪補充時用文字搜尋定位，不用固定索引 |
| 表格合併儲存格重複出現 | python-docx 的表格行為 | 用 cell.text 比對即可，修改時只改一次 |
| 中文字型未正確套用 | python-docx 的 font.name 只設 ASCII | 需額外 `rFonts.set(qn('w:eastAsia'), '字型名')` |
| 螢光筆不顯示 | python-docx 沒有內建 highlight API | 必須用 XML 操作：OxmlElement('w:highlight') |
| PDF 逐字稿文字有誤 | 語音辨識的同音字錯誤 | 根據上下文修正，以語意為準 |

---

## 完整流程圖

```
┌─────────────────────────────────────────┐
│  輸入：舊版.docx + 新版.docx           │
│  （可選）PDF逐字稿                      │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼──────────┐
    │ Step 1: 提取文字     │
    │   - 段落 + 表格      │
    │   - 舊版 & 新版      │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │ Step 2: 比對差異     │
    │   - SequenceMatcher  │
    │   - 段落 + 表格 Diff │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────────────────┐
    │ Step 3: 在新版上標註修改         │
    │   - Document('新版.docx')       │
    │   - 紅色(修改) / 灰色(舊文字)   │
    │   - 另存為「標註版.docx」        │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │ Step 4 (可選): PDF 補充          │
    │   - 提取PDF → 摘要要點           │
    │   - 與標註版比對遺漏             │
    │   - 綠色補充 → 覆寫標註版        │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────┐
    │  產出：標註版.docx   │
    │  + 比對摘要(Artifact)│
    └─────────────────────┘
```

---

## 產出物清單

1. **標註版 DOCX**：帶有紅色/綠色標記的完整文件
2. **比對摘要 (Markdown Artifact)**：列出所有修改處的一覽表，含表格說明

---

## 前置需求

```bash
pip3 install python-docx pdfplumber
```

如果 `pdfplumber` 無法安裝，可用 `PyPDF2` 作為備選。

---

## 使用範例

使用者可能的指令：
- 「請比對這兩個檔案，將修改的地方標註」
- 「請參考這份會議逐字稿，看有沒有漏掉的部份」
- 「某某會議之後的內容不要列入」

Agent 應依照本 Skill 的 SOP 逐步執行。
