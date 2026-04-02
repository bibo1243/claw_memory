---
name: aurora-hr-ops
description: 用於這個環境中的 Aurora/震旦 HR 作業，特別是根據本機文件與真實系統截圖製作 Word 或圖片教學卡、將流程步驟對齊到實際頁面、管理共用設定 > 權限管理 > 員工行動裝置帳號設定中的 LINE/App 權限，以及操作 HRHB007S00 的已驗證排班流程，包含 4 週週期排班與 ba000 多段班日編輯。
---

# Aurora HR 作業

這個 skill 主要處理三類重複性工作：

1. Aurora/震旦 HR 頁面與簽核流程的教學卡。
2. 在已驗證的管理頁面上處理員工 LINE/App 行動帳號。
3. 在已驗證的 `HRHB007S00.aspx` 頁面進行排班，包含週期排班與單日 `ba000` 多段班編輯。

請先閱讀 [references/repo_workflows.md](references/repo_workflows.md)，裡面有這個 repo 的固定路徑、已驗證頁面路由，以及在這個環境中已使用過的檔案。

## 教學卡

- 以使用者指定的來源事實為準：Word、既有截圖與本機 markdown 匯出檔。
- 在這個 repo 中，先檢查以下來源：
  - 使用者提供的 Word/docx 附件
  - `系統導航樹狀圖`
  - `output/INDEX.md` 與相關 markdown 匯出檔
  - 如果有，先看現有的根目錄腳本
- 設計教學卡前，務必把每一步對應到實際 Aurora 畫面。
- 優先使用真實系統截圖，不要只用很小的參考縮圖。
- 如果使用者要 Word 輸出，就建立 `.docx` 版本，並保留較大的截圖。
- 如果使用者不要「如圖」或參考縮圖條帶，就拿掉裝飾性的縮圖區塊，只保留流程內容與實際截圖。
- 如果截圖太糊，就用更大的視窗重新擷取，或改用原始匯出的圖片，不要把很多小圖硬縮成一條。

## 重用既有腳本

在 `/Users/leegary/小程序/elearning_scraper` 內作業時，如果已驗證過的腳本符合需求，優先重用 repo 根目錄的腳本：

- `make_teaching_cards.py`
- `make_line_signing_guide.py`
- `aoacloud_capture.py`
- `apply_schedule_liu_202603.py`

請搭配參考檔，使用這個 repo 裡已經證實有用的本機文件路徑。

## LINE 帳號管理

- 已驗證的管理頁面：`共用設定 > 權限管理 > 員工行動裝置帳號設定`
- 這個租戶的已驗證網址樣式：`AUAU002S00.aspx`
- 請使用可見的 DataTables 搜尋欄位 `input[type="search"][aria-controls="DataTables_Table_0"]`
- 不要用像 `MainContent_OrgCtrl_txtEmp` 這類隱藏欄位做列查找
- `enable-line` 代表勾選該列綁定 `GetPeople.IsLine` 的核取方塊並存檔
- `unbind-line` 代表先點綠色 `取消註冊`，再按頁面跳窗的 `確定`，接著按成功視窗的 `OK`，最後重新整理並驗證
- 開啟 LINE 權限不等於完成 LINE 綁定；權限開啟後，員工仍需在 `震旦HR系統` 對話中完成 LINE 端登入/綁定

若要穩定執行，請使用 [scripts/mobile_account_admin.py](scripts/mobile_account_admin.py)。

## 排班作業

- 這個租戶已驗證的頁面網址：`https://erp3.aoacloud.com.tw/HR/HRHB007S00.aspx`
- 使用者提到排班設定、週期排班、4 週彈性排班或 `ba000` 多段班時，請參考 [references/work_scheduling.md](references/work_scheduling.md)。
- 已驗證的 4 週排班請使用週期模式，不要假設一般月檢視一定能通過這些員工的法定休息驗證。
- 月格批次作業時，優先一次載入整批員工，依班別分組點選，最後一次存檔，不要每一格都存。
- 若是單日多段班編輯，先把目標日期轉成 `ba000`，再用 `GoToDayMode()` 切到日模式，然後更新 `vm.Day.Rows`。
- 日模式中已驗證的列查找方式是 `Name` 或 `Empno`，不是 `EmpnoName`。

若要穩定執行，請使用 [scripts/work_schedule_admin.py](scripts/work_schedule_admin.py)。

## 驗證

- 每次管理操作後，都要重新整理頁面並再次搜尋員工
- `enable-line` 後，要驗證 LINE 核取方塊仍維持勾選，且綠色 `取消註冊` 有出現
- `unbind-line` 後，要驗證成功視窗有出現，且重新整理後 `取消註冊` 不再顯示
- 每次存檔後排班，都要重新整理並從頁面資料驗證已保存的週期/日資料，不要只看草稿狀態
- 若結果會拿來做教學或給使用者確認，請保留截圖

## 敏感資料

- 不要擷取或揭露密碼、身分證字號或其他敏感識別資料
- 這個 skill 只限於頁面導覽、權限狀態、綁定狀態、截圖、教學卡製作，以及使用者明確要求的排班作業
