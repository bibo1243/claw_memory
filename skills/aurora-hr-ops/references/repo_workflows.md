# Repo Workflows

This skill was created from the repo:

- `/Users/leegary/小程序/elearning_scraper`

## Local Sources

Use these local sources first when working in this repo:

- `/Users/leegary/小程序/elearning_scraper/附件一：簽核流程115.03.26.docx`
- `/Users/leegary/小程序/elearning_scraper/系統導航樹狀圖`
- `/Users/leegary/小程序/elearning_scraper/output`
- `/Users/leegary/小程序/elearning_scraper/make_teaching_cards.py`
- `/Users/leegary/小程序/elearning_scraper/make_line_signing_guide.py`
- `/Users/leegary/小程序/elearning_scraper/aoacloud_capture.py`
- `/Users/leegary/小程序/elearning_scraper/apply_schedule_liu_202603.py`

## Useful Docs

- `[員工行動裝置帳號設定新增至收藏稍後觀看分享QR code列印](/Users/leegary/小程序/elearning_scraper/output/震旦雲HR系統-線上課程/HR系統操作專區/員工行動裝置帳號設定新增至收藏稍後觀看分享QR code列印.md)`
- `[LINE、APP打卡_考勤申請_簽核操作手冊新增至收藏稍後觀看分享QR code常見 Q&A列印](/Users/leegary/小程序/elearning_scraper/output/震旦雲HR系統-線上課程/HR系統操作專區/LINE、APP打卡_考勤申請_簽核操作手冊新增至收藏稍後觀看分享QR code常見 Q&A列印.md)`
- `[用LINE送請假單新增至收藏稍後觀看分享QR code列印](/Users/leegary/小程序/elearning_scraper/output/震旦雲HR系統-線上課程/HR系統操作專區/用LINE送請假單新增至收藏稍後觀看分享QR code列印.md)`
- `[出勤參數設定- 多段班(ba000)各段依規則自動扣休息時間新增至收藏稍後觀看分享QR code列印](/Users/leegary/小程序/elearning_scraper/output/震旦雲HR系統-線上課程/HR系統操作專區/出勤參數設定- 多段班(ba000)各段依規則自動扣休息時間新增至收藏稍後觀看分享QR code列印.md)`
- `[01-共用設定](/Users/leegary/小程序/elearning_scraper/系統導航樹狀圖/notebooklm/01-共用設定.md)`

## Verified Page Route

- Menu path: `共用設定 > 權限管理 > 員工行動裝置帳號設定`
- URL seen in this tenant: `https://erp3.aoacloud.com.tw/AU/AUAU002S00.aspx`
- Working row filter selector: `input[type="search"][aria-controls="DataTables_Table_0"]`

## Verified Work Scheduling Route

- Page URL in this tenant: `https://erp3.aoacloud.com.tw/HR/HRHB007S00.aspx`
- Working employee selector: `#WorkScheduleOrgCtrl_Emp`
- Cycle selector is driven by `vm.query.GroupByCycle`
- The validated March 2026 flexible-schedule cycle was `n472` for `2026/03/12~2026/04/08`
- Day-mode multi-segment editing requires converting the target day to `ba000` first, then entering `GoToDayMode()`

## Verified Behaviors

- Unbinding LINE works by pressing the green `取消註冊`, then the page modal `確定`, then the success modal `OK`
- Enabling LINE capability works by checking the `GetPeople.IsLine` checkbox for the employee row and clicking `存檔`
- A successful LINE capability enable shows the checkbox still checked after reload and usually restores the green `取消註冊`
- Capability enable does not finish LINE binding; the employee still needs to complete login/binding in the LINE-side `震旦HR系統` flow

## Verified Work Scheduling Behaviors

- For the March 2026 `劉春燕(302)` case, cycle scheduling saved successfully only after switching to the 4-week cycle view
- The validated pattern was:
  - weekdays: `b0027` (`晚餐膳務 12:00~20:30`)
  - Saturdays: `kd=4` (`休息日`)
  - Sundays: `kd=0` (`例假`)
- A validated single-day `ba000` edit was saved for `2026/03/25` with:
  - `08:00-12:00`
  - `18:00-23:00`
- Day-mode row lookup should use `Name` or `Empno`; `EmpnoName` is not present there
- Day-mode save returned `200` from `api/WorkScheduleMulti/Save`

## Teaching Card Notes

- The user preferred Word-based teaching cards when screenshots needed to stay legible
- The user rejected decorative "如圖/參考畫面" thumbnail strips and wanted real page screenshots instead
- For manager LINE approval cards, the screenshots from the LINE manual were clearer than shrinking desktop screenshots
