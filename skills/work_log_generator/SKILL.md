---
name: Work Log Generator
description: 從 Notion 任務資料庫彙整當日任務，產出符合機構格式的表格式 Word 工作日誌。採用三欄表格（項目、內容、進度）搭配分類標題列，內含自動大綱編號、標楷體排版與可點擊超連結。
---

# Work Log Generator（工作日誌產出器）

## 📌 用途

從 Notion 任務資料庫中擷取當日已完成或進行中的任務，經由 Markdown 草稿確認後，自動產出符合慈光基金會格式規範的 Word 工作日誌（.docx）。

---

## 🏗️ 文件格式規範（基於正式範本）

### 文件結構

```
┌────────────────────────────────────────────────────────────┐
│        財團法人台中市私立慈光社會福利慈善事業基金會           │  ← 機構名稱（16pt 粗體、置中）
│                        工作日誌                              │  ← 標題（16pt 粗體、置中）
│                                                            │
│  年度：115年　　　日期：115年03月06日    填表人：李冠葦       │  ← 資訊行（12pt、左對齊）
├────────────┬─────────────────────────────┬───────────────┤
│    項目    │            內容               │     進度      │  ← 表格標題列（灰底、粗體、置中）
├────────────┼─────────────────────────────┼───────────────┤
│ 🟦 行政組事務                                      │  ← 分類標題列（合併3欄、淺灰底 F2F2F2、14pt 粗體、置中）
├────────────┼─────────────────────────────┼───────────────┤
│ 任務名稱₋₂₀₂₆.₀₃.₁₉₍四₎│ 詳細內容說明...   │  待辦理/已完成 │  ← 資料列（日期後綴以下標呈現）
└────────────┴─────────────────────────────┴───────────────┘
```

### 字型與基本設定

| 項目         | 規格                |
| ------------ | ------------------- |
| 字型         | 標楷體（含東亞字元）  |
| 機構名稱/標題 | 16pt 粗體           |
| 資訊行       | 12pt                |
| 分類標題     | 14pt 粗體            |
| 表格標題列   | 12pt 粗體            |
| 內文         | 11pt                |
| 行距         | 1.15 倍（緊湊）      |
| 頁面邊距     | 上下左右 2.54cm      |

### 表格欄位設定

| 欄位 | 寬度 (cm) | 對齊方式 | 說明                                    |
| ---- | --------- | -------- | --------------------------------------- |
| 項目 | ≈4.0      | 左對齊   | 任務名稱 + 日期下標後綴                   |
| 內容 | ≈9.5      | 左對齊   | 詳細說明，含辦理情形、附件超連結等        |
| 進度 | ≈2.5      | 置中     | 狀態標註（如「待辦理」、「已完成」、「持續追蹤中」） |

> ⚠️ **欄寬合計不可超過 A4 頁面可用寬度（約 16.5cm）**。
> 原設定 4.5+13.0+2.5=20cm 會超出版面，導致進度欄右側被裁切。

### 分類行（Category Row）

- **合併 3 欄**為一整行
- **粗體文字 + 淺灰背景**（Hex: F2F2F2）
- **14pt 字型 + 置中對齊**
- 分類名稱由 Agent 依當日實際任務內容動態決定，**不需要每次都相同**
- 常見分類參考（可按需求增減）：
  - 行政組事務
  - 人資組事務
  - 會計室事務
  - 總務組事務
  - 跨部門協作
  - 其他
  - 每週反思（選用）

### 項目欄日期後綴格式

- 每個任務項目標題若尾部帶有日期（如 `115.03.09` 或 `2026.03.09`），需自動拆分
- **日期部分以下標（subscript）呈現**，格式為：`-YYYY.MM.DD（星期）`
- 下標字型大小：**8pt**（比主文 12pt 明顯更小）
- 範例：`擬定加班制度` → 主文字 12pt + 下標 `-2026.03.09（一）` 8pt
- 此功能由 `_split_title_and_date()` 函數自動處理

### 每個任務的「內容」欄結構（多層自動大綱編號）

內容欄支援 **Word 內建自動大綱編號**，六層架構：

```
一、  ← Level 0: taiwaneseCounting, 12pt, 粗體
  （一）  ← Level 1: taiwaneseCounting + 括號, 12pt
    1.  ← Level 2: decimal, 12pt
    （1）  ← Level 3: decimal + 括號, 12pt
      a.  ← Level 4: lowerLetter, 12pt
      (a)  ← Level 5: lowerLetter + 括號, 12pt
```

> ⚠️ **必須使用 Word 內建的自動大綱編號**（`apply_numbering_to_paragraph()`），不可手動打字編號。
> 當切換到新的上層時（例如新的「（一）」），需呼叫 `reset_outline_at_level()` 重設子層計數器。

使用範例：

```
一、整體概要
  （一）導入背景
    1. 完成需求訪談
    2. 確認預算方案
  （二）人員培訓
    1. 安排教育訓練            ← 1. 從頭開始（因為切換到新的（二））
      （1）具體步驟
        a. 第一小步
          (a) 子細節
附件：🔗 檔案名稱 (Google Drive)   ← 可點擊超連結
```

**注意**：此格式與參考範本一致，不使用「辦理情形」的行首格式，而是將狀態顯示在「進度」欄位。

### 超連結處理

- **Word 文件中的附件連結必須是可點擊的超連結**（藍色、帶底線）
- 使用 `python-docx` 的 hyperlink XML 實作，不可僅存為純文字
- 連結目標通常為 Google Drive 的分享連結

---

## 📝 Markdown 草稿格式（中間產物）

### 用途

在產出最終 Word 前，先讓使用者閱讀確認內容。草稿檔使用 Markdown 格式撰寫。

### 命名慣例

```
{YYYY-MM-DD}_WorkLog_Draft.md
```

### 草稿結構

草稿中使用**縮排標記**來對應大綱層級：

```markdown
# 2026.03.06 工作日誌

## 行政組事務                    ← 分類標題（對應表格的分類行）
#### 任務標題名稱 115.03.06       ← 任務名稱（對應「項目」欄，尾部日期會變下標）
- **進度**：待辦理/已完成        ← 進度欄位
- L0: 整體工作概要               ← 大綱 Level 0 (一、)
  - L1: 導入背景                     ← 大綱 Level 1 (（一）)
    - L2: 完成需求訪談                ← 大綱 Level 2 (1.)
    - L2: 確認預算方案                ← 大綱 Level 2 (2.)
  - L1: 人員培訓                     ← 大綱 Level 1 (（二）)
    - L2: 安排教育訓練              ← 大綱 Level 2 (1.) ← 重新計數
      - L3: 具體步驟                  ← 大綱 Level 3 (（1）)
        - L4: 第一小步              ← 大綱 Level 4 (a.)
          - L5: 子細節            ← 大綱 Level 5 ((a))
- **附件**：[🔗 檔案名稱](https://drive.google.com/...)

## 其他                          ← 另一個分類
#### 另一個任務名稱
- **進度**：持續追蹤中
- L0: 說明內容...
```

### 層級對應

| Markdown 語法              | 對應表格元素           | 大綱編號    |
| -------------------------- | ---------------------- | ----------- |
| `## 分類名稱`              | 分類行（合併 3 欄灰底） | —          |
| `#### 任務標題 115.03.06`  | 項目欄 + 日期下標       | —          |
| `- **進度**：...`          | 進度欄                 | —          |
| `- L0: 文字`              | 內容欄                 | 一、        |
| `  - L1: 文字`            | 內容欄                 | （一）      |
| `    - L2: 文字`          | 內容欄                 | 1.          |
| `      - L3: 文字`        | 內容欄                 | （1）        |
| `        - L4: 文字`      | 內容欄                 | a.          |
| `          - L5: 文字`    | 內容欄                 | (a)         |
| `- **附件**：[文字](URL)` | 內容欄附件行           | —          |

---

## 🔄 完整作業流程（SOP）

### 步驟一：從 Notion 擷取任務

1. 使用 Notion MCP 的 `query-data-source` 查詢任務資料庫
2. 篩選條件：
   - 完成日期或更新日期落在目標日期
   - 狀態為「Done」或「In Progress」或相關狀態
3. 取得每筆任務的標題、狀態、描述等資訊
4. 若任務有細節頁面，進一步使用 `get-block-children` 取得頁面內容

### 步驟二：分類整理

1. 依任務性質分類到適當的類別（參考上方常見分類）
2. 確認每個任務的：
   - 說明（完整描述，不要空泛）
   - 進度（待辦理/已完成/持續追蹤中）
   - 附件（找出本地對應檔案 → 比對 Google Drive 同步連結）

### 步驟三：產出 Markdown 草稿

1. 建立 `{YYYY-MM-DD}_WorkLog_Draft.md`
2. 按照上方草稿格式撰寫
3. **請使用者確認草稿內容**（這步必做）

### 步驟四：附件連結處理

1. 查找本地檔案路徑（通常在 `~/個人app/個人資料夾/` 下）
2. 對應 Google Drive 的雲端路徑，取得分享連結
3. 將連結嵌入 Markdown 草稿中

### 步驟五：產出 Word 文件

1. 執行 `scripts/gen_work_log_table.py` 腳本（見下方說明）
2. 輸入：Markdown 草稿路徑
3. 輸出：`{YYYY.MM.DD}_工作日誌.docx` → 存放至 `~/個人app/個人資料夾/工作日誌/`

---

## 🛠️ 技術實作要點

### 使用 python-docx

```bash
pip3 install python-docx
```

### 表格建立核心邏輯

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import OxmlElement, parse_xml

# 初始化大綱編號引擎（必須在建表前）
init_outline_numbering(doc)

# 建立表格（3 欄）
table = doc.add_table(rows=1, cols=3, style='Table Grid')

# 設定欄寬（合計不可超過 16.5cm）
widths = [Cm(4.0), Cm(9.5), Cm(2.5)]
for i, width in enumerate(widths):
    table.columns[i].width = width
```

### 分類行（跨欄合併）的實作

> ⚠️ **python-docx 合併儲存格的常見陷阱**
>
> `table.add_row()` 會建立 N 個 `<w:tc>` 元素。**只設 `gridSpan` 不會自動移除多餘的 `<w:tc>`**，
> 必須手動 `tr.remove(tc)` 才能真正合併。否則 Word 會把多餘的 `<w:tc>` 當作額外格子渲染，
> 導致分類標題列看起來格式異常（雖然第一格有 gridSpan=3，但後面還有 2 個空白格子）。
>
> **正確四步驟**：
> 1. `table.add_row()` → 此時有 N 個 `<w:tc>`
> 2. `tr.remove(tc)` → 移除多餘的 `<w:tc>`，只保留第 1 個
> 3. 設定 `gridSpan = N` → 在保留的 `<w:tc>` 上宣告佔幾欄
> 4. 設定格式與內容 → 對唯一的 cell 設定文字、字型、底色

```python
def add_category_row(table, category_name):
    """新增分類標題行（合併3欄、淺灰底、置中、14pt粗體）"""
    row = table.add_row()

    # 🔑 關鍵：從 XML 層級移除多餘的 <w:tc>，只保留第一個
    tr = row._tr
    tcs = tr.findall(qn('w:tc'))
    for tc in tcs[1:]:       # 移除第 2、3 個 <w:tc>
        tr.remove(tc)

    # 設定 gridSpan 合併三欄
    cell = row.cells[0]
    tcPr = cell._tc.get_or_add_tcPr()
    gridSpan = OxmlElement('w:gridSpan')
    gridSpan.set(qn('w:val'), '3')
    tcPr.append(gridSpan)

    # 設定文字
    cell.text = category_name

    # 設定淺灰底色
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'F2F2F2')
    cell._tc.get_or_add_tcPr().append(shading_elm)

    # 設定文字格式
    for para in cell.paragraphs:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.font.name = '標楷體'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '標楷體')
            run.font.size = Pt(14)
            run.bold = True
```

### 表格標題列格式（灰底 D9D9D9）

```python
# 表格標題列
hdr_cells = table.rows[0].cells
for cell in hdr_cells:
    # 設定灰底
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'D9D9D9')
    cell._tc.get_or_add_tcPr().append(shading_elm)
    
    # 設定置中粗體
    for para in cell.paragraphs:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.font.name = '標楷體'
            run.font.size = Pt(12)
            run.bold = True
```

### 超連結實作（可點擊）

```python
def add_hyperlink(paragraph, text, url):
    """新增可點擊的超連結"""
    part = paragraph.part
    r_id = part.relate_to(
        url,
        docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK,
        is_external=True
    )
    
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    # 設定藍色+底線
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    rPr.append(color)
    
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    
    paragraph._p.append(hyperlink)
    return hyperlink
```

### 內容欄套用大綱編號

```python
# 在內容欄的段落中套用自動編號
cell = row.cells[1]

p1 = cell.paragraphs[0]
add_run_to_paragraph(p1, '系統導入相關')
apply_numbering_to_paragraph(p1, 0)  # 一、

p2 = cell.add_paragraph()
add_run_to_paragraph(p2, '導入背景')
apply_numbering_to_paragraph(p2, 1)  # （一）

p3 = cell.add_paragraph()
add_run_to_paragraph(p3, '完成需求訪談')
apply_numbering_to_paragraph(p3, 2)  # 1.

# 切換到新的（二）時，重設 1. 的計數器
reset_outline_at_level(2)
p4 = cell.add_paragraph()
add_run_to_paragraph(p4, '人員培訓')
apply_numbering_to_paragraph(p4, 1)  # （二）
```

### 踩坑記錄

| 問題 | 原因 | 解法 |
|------|------|------|
| 編號後出現大段 Tab 空白 | Word 預設後置字元為 Tab | 加入 `<w:suff w:val="nothing"/>` |
| 每個（一）下的 1. 不從頭開始 | 同一 numId 的計數器會持續累加 | 使用 `lvlOverride` + `startOverride` |
| 分類列合併異常 | 只設 gridSpan 未移除多餘 tc | `tr.remove(tc)` 移除多餘元素 |
| 欄寬超過 A4 頁面 | 4.5+13+2.5=20cm 超過 16.5cm | 改用 4.0+9.5+2.5=16cm |
| 字型未套用到東亞字元 | python-docx 的 font.name 只設 ASCII | 額外設定 rFonts.eastAsia |
