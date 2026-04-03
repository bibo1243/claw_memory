# 🤖 Agent Skills (核心技能) 總目錄

這份目錄自動整理了系統中所有建立的 Skill 功能說明及最後修改時間，幫助你快速對照「英文資料夾」與「實際中文功能」。每次我想起或更新新技能時，你可以隨時來這裡查看。

> **分類說明**：`_custom/` 為 Gary 自創的 Skill；`_external/` 為外部下載的第三方 Skill。

---

## 🛠️ 自創 Skill (`_custom/`)

| 英文資料夾名稱 (Folder) | 中文名稱 / 功能簡介 | 最後更新時間 |
| :--- | :--- | :--- |
| **`4d_workflow_backend_architecture`** | **4D Workflow Backend Architecture & Sync**<br>負責維護 4D Workflow 的後端雙向同步機制，包含 Notion 與 Google Calendar 整合架構、資料過濾及樂觀更新 (Optimistic UI) 預想。完整 API 端點表、`/api/convert` 端點說明、後端重啟 SOP。 | 2026-03-06 |
| **`4d_workflow_convert_feature`** | **4D Workflow GCal ↔ Notion 互轉功能**<br>記錄 GCal 與 Notion 雙向搬移互轉功能的完整實作架構、前後端協作模式、常見坑點（dnd-kit 事件攔截、孤兒代碼、後端重啟）與除錯 SOP。 | 2026-03-06 |
| **`annual_plan_consistency`** | **Annual Plan Consistency Manager**<br>負責維護 Gary 2026 年度計畫相關系列檔案的一致性。確保當目標標題、里程碑或核心內容在其中一個檔案修改時，其他關聯檔案也能同步連動。 | 2026-03-04 |
| **`core_leadership_styles`** | **Core Leadership Styles**<br>記錄三位核心主管的督導、溝通風格與常見思維模式，用於輔助對話、參與決策或起草訊息時參考。 | 2026-02-28 |
| **`core_meeting_coordinator`** | **Core Meeting Coordinator**<br>協助處理「慈光核心會議」的協調、確認與通知擬稿。 | 2026-03-01 |
| **`docx_diff_annotator`** | **DOCX Diff Annotator**<br>比對兩份 Word 文件（新舊版），在不變更原始格式的前提下，以色彩標註修改處；並可從 PDF 會議逐字稿中擷取遺漏的討論要點補充標註。 | 2026-03-08 |
| **`gdrive_direct_sync`** | **Google Drive Direct Sync Protocol**<br>處理 Google Drive 與本地端檔案同步的核心準則，繞過桌機版自動同步延遲問題。 | 2026-03-03 |
| **`google_calendar_manager`** | **Google Calendar Manager**<br>透過 Google Calendar MCP 讀寫使用者的 Google 行事曆。 | 2026-02-28 |
| **`inbox_organizer`** | **Inbox Organizer**<br>處理並歸類放到 Inbox 目錄中的檔案。會根據檔案內容或檔名自動找尋或建立分類。 | 2026-03-02 |
| **`just_do_it_annual_plan`** | **Just Do It Annual Plan Method**<br>《只管去做》（邹小强著）的「著陸式年度計畫法」核心方法論，涵蓋從願景→目標→計畫→習慣→每日執行的完整流程。 | 2026-03-04 |
| **`keyword_manager`** | **Keyword Manager**<br>管理系統內使用的統一標籤與關鍵字清單，確保跨平台標籤一致性。 | 2026-02-26 |
| **`leave_schedule_reader`** | **Leave Schedule Reader**<br>讀取基金會假表（Google Sheets）的結構與規則，用於查詢同仁排休、值班安排。 | 2026-03-01 |
| **`line_local_reader`** | **LINE Local Reader**<br>讀取並摘要存放在電腦本地的 LINE 備份訊息 (HTML 格式)。 | 2026-03-02 |
| **`meeting_minutes_generator`** | **Meeting Minutes Generator**<br>從逐字稿與議程等來源，產出符合正式公文格式的 Word 會議紀錄。 | 2026-03-01 |
| **`multi_agent_file_collaboration`** | **Multi-Agent File Collaboration**<br>多智能體協作編輯同一份文件時的分工策略、衝突預防機制與合併流程。確保兩台以上 AI 實例同時作業時不會互相覆蓋內容。 | 2026-03-08 |
| **`notion_workspace`** | **Notion Workspace & Core Rules**<br>Gary 的 Notion 工作區架構、行為準則、任務管理規則、記帳規則。 | 2026-02-28 |
| **`org_operation_db`** | **Organization Operation Database Manager**<br>自動提取工作日誌中的管理經驗、底層邏輯洞察，累積至「組織運作資料庫」。 | 2026-03-03 |
| **`organization_knowledge`** | **Organization Knowledge**<br>慈光基金會暨附設機構的組織架構、人員編制、員工手冊位置等核心知識。 | 2026-02-28 |
| **`proposal_plan_generator`** | **Proposal Plan Generator**<br>為慈馨兒少之家產出正式的「計畫書」Word 文件（如物資需求申請、設備改善計畫等）。依照機構既定格式、公文書寫慣例與過往修訂經驗，直接輸出可送簽的 DOCX 檔案。 | 2026-03-22 |
| **`react_history_immunity`** | **React History Immunity (Undo/Redo)**<br>處理 React 嚴格模式與重複渲染事件下的 undo/redo 歷史堆疊「深層免疫」架構原則。 | 2026-03-05 |
| **`safe_delete_policy`** | **Safe Delete Policy**<br>核心安全準則：任何檔案刪除或覆寫前，必須先取得明確同意。 | 2026-02-26 |
| **`shared_memory_system`** | **共享記憶系統**<br>多智能體協作的核心知識庫。管理技能註冊、經驗記錄、通訊機制，確保 Trae 與 Antigravity 等 AI 實例能共享知識與記憶。 | 2026-03-08 |
| **`erjia-schedule-converter`** | **兒家班表轉檔**<br>專門將兒家班表 PDF 轉成可編輯的 Excel，保留日期、班別、多行儲存格、白/紅/藍底語意與排班規則，適合兒家、保育、生輔股輪值表分析與復刻。 | 2026-03-29 |
| **`skill_directory_manager`** | **Skill Directory Manager**<br>負責維護「Agent Skills 總目錄表」。只要有新增、刪除或修改任何 Skill，必須確保同步更新目錄。 | 2026-03-03 |
| **`skill-discovery-policy`** | **Skill Discovery Policy**<br>管理多 IDE / 多 agent 的技能檢索規則。定義 GitHub skills 為唯一權威來源、何時可快速檢索、何時必須完整掃描，以及回答技能存在與否時的固定格式。 | 2026-04-03 |
| **`smart_goal_reviewer`** | **SMART Goal Reviewer**<br>運用 SMART 原則審核年度目標的具體性、可衡量性、可達成性、相關性與時限性。 | 2026-03-04 |
| **`star_office_ui`** | **Star Office UI Manager**<br>管理像素辦公室看板 (Star Office UI)，同步 Agent 狀態與昨日小記。 | 2026-03-02 |
| **`super_individual_manager`** | **Super Individual Archive Manager**<br>負責追蹤與記錄 Gary 的個人反思、成長與身心健康軌跡，存入超級個體檔案庫。 | 2026-03-03 |
| **`things_gtd_manager`** | **Things GTD Manager**<br>透過 AppleScript 管理 Things 3 任務（觸發詞 "@@"）。 | 2026-03-01 |
| **`underlying_logic`** | **Underlying Logic Framework**<br>運用劉潤《底層邏輯》的五大高維度思維模型，在面對複雜問題時看穿事物本質。 | 2026-03-03 |
| **`vite_nohup_execution`** | **Vite Nohup Background Execution**<br>解決利用 nohup 在背景啟動 Vite 前端伺服器時的正確啟動策略。 | 2026-03-06 |
| **`work_log_generator`** | **Work Log Generator**<br>從 Notion 任務資料庫彙整當日任務，產出符合機構格式的表格式 Word 工作日誌。 | 2026-03-06 |
| **`youtube_transcriber`** | **YouTube Transcriber**<br>透過 YouTube 字幕 API 擷取影片逐字稿，並總結為精華重點筆記。 | 2026-03-09 |

---

## 🔽 外部下載 Skill (`_external/`)

| 英文資料夾名稱 (Folder) | 中文名稱 / 功能簡介 | 來源 | 最後更新時間 |
| :--- | :--- | :--- | :--- |
| **`gog-1.0.0`** | **Google Workspace CLI**<br>Google Workspace 相關的 CLI 操作工具。 | 第三方 Skill | 2026-03-09 |
| **`proactive-agent-3`** | **Proactive Agent**<br>能記住使用者人設並預測接下來可能的行動，讓 AI 更主動、更聰明。 | 第三方 Skill | 2026-03-09 |
| **`summarize-1`** | **Summarize CLI**<br>直接總結 YouTube 影片等長內容的精華，支援追問與執行建議。 | 第三方 Skill | 2026-03-09 |
| **`tavily-search-1.0.0`** | **Tavily Search**<br>Tavily 搜尋引擎整合，可搜尋網路上的即時資訊。 | 第三方 Skill | 2026-03-09 |
| **`ui-ux-pro-max-skill-2.2.1`** | **UI/UX Pro Max**<br>進階 UI/UX 設計框架與模式庫，提供專業級的介面設計指引。 | 第三方 Skill | 2026-03-09 |
| **`openclaw-skills-word-docx`** | **DOCX Word 文件專家**<br>讀取與生成 Word (.docx) 檔案的專業知識庫。理解 ZIP/XML 底層結構（runs、paragraphs、sections、styles），支援模板驅動文件生成、格式清理、修訂追蹤、頁首頁尾、複雜編號系統等。 | LobeHub Marketplace v1.0.1 | 2026-03-10 |

---

## 📁 專案與程式開發技能 (位於 `年度計畫/年度目標/.agent/skills/`)

這些技能主要是在 2026 年 2 月中旬建立，用於輔助前端 Web App、行事曆應用程式的系統架構開發。

| 英文資料夾名稱 (Folder) | 中文名稱 / 功能簡介 | 最後更新時間 |
| :--- | :--- | :--- |
| **`calendar_browser_testing`** | **calendar_browser_testing**<br>行事曆應用的瀏覽器操作與測試指南。 | 2026-02-16 |
| **`calendar_dark_theme`** | **calendar_dark_theme**<br>行事曆暗色主題的 CSS 覆蓋架構與變數系統規則。 | 2026-02-16 |
| **`calendar_datetime_standard`** | **calendar_datetime_standard**<br>處理日期與時間的標準規則，區分全天與特定時間事件。 | 2026-02-16 |
| **`calendar_event_card`** | **calendar_event_card**<br>EventCard 編輯模式與時間軸背景的架構與互動邏輯。 | 2026-02-16 |
| **`calendar_grid_view`** | **calendar_grid_view**<br>萬年曆（月曆格子視圖）的架構、資料流與 CSS 慣例。 | 2026-02-16 |
| **`calendar_tag_system`** | **calendar_tag_system**<br>行事曆標籤（Tag）系統的架構、資料模型與開發準則。 | 2026-02-16 |
| **`docx_calendar_parser`** | **docx_calendar_parser**<br>安全且準確地從 Word 表格中提取行事曆資料。 | 2026-02-16 |
| **`snapshot_manager`** | **Snapshot Manager**<br>用於備份和還原關鍵檔案的技能，特別是在重大修改前。 | 2026-02-16 |
| **`wysiwyg-markdown-editor`** | **WYSIWYG Markdown Editor**<br>基於 Tiptap 的 Markdown 編輯器引擎設定與架構。 | 2026-02-16 |
