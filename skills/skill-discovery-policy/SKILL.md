---
name: Skill Discovery Policy
description: 管理多 IDE / 多 agent 的技能檢索規則。定義 GitHub skills 為唯一權威來源、何時可快速檢索、何時必須完整掃描，以及回答技能存在與否時的固定格式，避免只靠少數示例 skill、單次 grep 或 session 記憶下結論。
---

# Skill Discovery Policy

此技能用來治理「如何找技能」與「如何回答技能是否存在」。

適用情境：

- 使用者詢問「你現在有哪些技能」
- 使用者詢問「有沒有某類技能」
- 使用者詢問「有沒有理財 / 記帳 / 預算 / 管理 / 溝通 / 自動化相關技能」
- 使用者要求列出某能力對應的 skill 與位置
- 多 IDE / 多 agent 容易因為本地副本、快取、示例 skill 或抽樣檢索而得出錯誤結論

## Source of Truth

1. 自訂 skills 的唯一權威來源是 GitHub repo `https://github.com/bibo1243/claw_memory`。
2. 正式內容以 repo 根目錄 `skills/` 為準。
3. 若當前環境已有本地 clone，優先使用該 clone 的 `skills/`。
4. 不得把 OneDrive、IDE 私有副本、快取、舊備份或其他散落目錄當成正式技能來源。

## 檢索分流規則

### A. 可使用快速檢索的情況

當使用者問的是明確、具體、名稱清楚、領域邊界狹窄的技能，可使用快速檢索：

- 震旦
- Aurora HR
- HRHB007S00
- Google Calendar
- Notion
- 某個明確 skill 名稱

快速檢索流程：

1. 列出 `skills/`
2. 用名稱與關鍵字篩選
3. 讀最相關的 1 到 3 份 `SKILL.md`
4. 直接回答結果

### B. 必須完整掃描的情況

當使用者問的是抽象能力、跨領域能力或泛類別能力，禁止只抽樣或只靠單次 grep：

- 理財
- 財務
- 記帳
- 預算
- 管理
- 溝通
- 領導
- 自動化
- 知識管理
- 決策支援

完整掃描流程：

1. 掃描所有可能相關的 skill 資料夾名稱
2. 檢查每個候選 skill 的 `SKILL.md` frontmatter
3. 檢查 `description`
4. 檢查內文中的規則、流程、資料庫、欄位、工具與操作說明
5. 必要時再查 `references/` 與 `scripts/`

## 判定原則

1. 回答時應先判斷「是否具備該能力」，不是只判斷「是否存在同名獨立 skill」。
2. 即使沒有名為 `finance`、`budget`、`accounting` 的獨立 skill，只要綜合型 skill 內承載該能力，也必須列出。
3. 若存在名稱或內容明確匹配的獨立 skill，必須優先列出，不可漏掉。
4. 禁止只依賴使用者先前列出的示例 skill。
5. 禁止只讀 3 到 4 份 `SKILL.md` 就對抽象能力下結論。

## 財務 / 理財專用規則

當使用者詢問財務、理財、記帳、預算、貸款、投資相關技能時：

1. 必須完整檢查所有與以下關鍵詞相關的 skill：
   `finance`, `budget`, `money`, `wealth`, `accounting`, `expense`, `income`, `asset`, `invest`, `loan`, `理財`, `財務`, `記帳`, `預算`, `投資`, `貸款`
2. 若存在獨立 skill，例如 `personal-finance`，必須先回報該獨立 skill。
3. 不可因為先找到 `notion_workspace`、`notion-integration`、`gtd-capture`、`discovery.md` 就提前停止。
4. 若同時存在獨立 skill 與綜合型 skill，兩者都要回答。

## 回答格式

除非使用者要求完整證據，預設回答格式固定為：

1. 一句話結論
2. `獨立 skill：...`
3. `綜合型 skill / 相關能力：...`
4. `位置：...`

預設不要展示：

- shell 指令
- grep 過程
- readfile 過程
- 大表格
- 長篇檢查報告

## 規則與資料的區分

若使用者詢問的是「目前有哪些預算項目」「目前有哪些財務資料」這類現況問題，必須區分：

1. 技能中定義的規則、欄位與流程
2. 真正的即時資料來源中的現況資料

若只查到 skill 規則，必須明確說「目前查到的是 skill 規則，不是當前資料」。

## 標準範例

### 範例 1：抽象能力

問題：`目前有沒有理財相關技能？`

標準回答：

`有。`

- `獨立 skill：personal-finance`
- `綜合型 skill / 相關能力：notion_workspace、notion-integration、gtd-capture、discovery.md (GAA 規格書)`
- `位置：repo skills/ 目錄下對應資料夾`

### 範例 2：明確系統

問題：`有沒有震旦系統的操作技能？`

標準回答：

`有。`

- `獨立 skill：aurora-hr-ops、aurora-hr-schedule-operator`
- `綜合型 skill / 相關能力：無`
- `位置：repo skills/ 目錄下對應資料夾`

## 禁止事項

1. 不可只用 skill 名稱或資料夾名稱就下結論。
2. 不可只靠單次 grep 命中與否回答抽象能力。
3. 不可把 session 記憶當成技能權威來源。
4. 不可忽略已存在的獨立 skill。
5. 不可把 skill 定義誤答成即時資料。
