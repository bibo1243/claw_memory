# 單日班別指派

當使用者要在 Aurora HR 內，針對某個目標日期替一位或多位員工指派正常班別時，請使用這份參考。

這份文件刻意寫得很明確，讓較弱的模型也能幾乎不靠即興推理就照著做。

下面的日期與姓名只是已驗證範例，不是硬編死的限制。相同方法可套用到任何有效目標日期與任何有效班別代碼。

## 範圍

這份參考涵蓋：

- 一位員工、一個日期、一個班別
- 多位員工、同一天、同一個班別
- 多個日期，只要你先拆成不同日期批次

這份參考**不**涵蓋：

- `ba000` 多段班編輯
- `排休` 模式下的假別/休息日平衡
- LINE 帳號管理
- 教學卡製作

## 日期防混淆守則

如果使用者提到多個日期，不要直接照句子做。先把需求改寫成扁平化的執行清單。

錯誤思維：

- `4/9 和 4/10 都要改`

正確的執行清單：

- 員工 A，`20260409`，班別 X
- 員工 B，`20260409`，班別 X
- 員工 A，`20260410`，班別 Y
- 員工 B，`20260410`，班別 Y

必要紀律：

1. 先把月/日寫法統一轉成 `YYYYMMDD`。
2. 一次只處理一個日期批次。
3. 完成一個日期批次後，重新開始下一個日期批次。
4. 在日誌、截圖與最終回報中，都要包含完整的正規化日期。

## 已驗證流程

對每一位員工，都請使用這個固定順序：

1. 登入。
2. 開啟 `HRHB007S00.aspx`。
3. 在 `#WorkScheduleOrgCtrl_Emp` 選擇員工。
4. 點 `加入`。
5. 檢查 `#selChangeUserCycRange`，並選出日期範圍包含目標日期的母週期。
6. 在頁面 JS 中，用 `Empno` 找到員工列。
7. 在 `row.DaysInfo` 中找到目標日期。
8. 設定工作模式：
   - `vm.controller.HoliDayClass = true`
   - `vm.controller.SelDutyClass = <shift code>`
   - `vm.chkDutyClass = true`
9. 對目標格子呼叫 `scope._SetClass(...)`。
10. 點 `#btnSave`。
11. 如果出現警告或成功跳窗，就按 `確定` / `OK`。
12. 重新整理頁面。
13. 重新加入員工。
14. 重新選週期。
15. 在重新載入後的頁面上驗證已保存的 `DaysInfo`。

如果有多位員工，請對每位員工重複完整的存檔、重新整理、驗證流程。不要把兩位員工混成一次存檔就假設兩個都成功。

## 為什麼要用 Empno

畫面上可見的標籤只用於 UI 選擇。資料列查找應該使用 `Empno`。

已驗證的列查找寫法：

```javascript
const row = vm.TableRowsDetail.find(r => r.Empno === targetEmpno);
```

不要依賴：

- `Name`
- `EmpnoName`

這些欄位在不同視圖裡可能是空值，或不一致。

## 如何推導正確週期

員工加入後，請檢查 `#selChangeUserCycRange`。

2026 年 4 月已驗證的選項例子：

- `n472` -> `2026/03/12~2026/04/08`
- `n473` -> `2026/04/09~2026/05/06`

規則：

- 選出第一個**母週期**，且其文字範圍包含目標日期
- 忽略文字開頭是 `-` 的子週選項

例如：

- 目標日期 `20260412` 落在 `2026/04/09~2026/05/06`
- 因此應使用 `n473`

## 班別設定

正常班別指派時，請先設定：

```javascript
vm.controller.HoliDayClass = true;
vm.controller.SelDutyClass = shiftCode;
vm.controller.SelAll = false;
vm.controller.SelHoliDayClass = '4';
vm.controller.SelHoliDayDutyClass = 'default';
vm.controller.SelLeaveClass = '';
vm.chkDutyClass = true;
vm.chkPstn = false;
vm.chkNotes = false;
vm.chkCostDpt = false;
vm.chkPlace = false;
vm.chkWorkHoliDay = false;
vm.HoliDayClassType = '0';
```

接著套用：

```javascript
scope._SetClass(cell, row.DaysInfo, idx, row.EmpnoName || row.Name, row);
```

## 已驗證範例：2026-04-12 李冠葦

目標：

- 員工：`李冠葦(101)`
- Empno：`0000000005`
- 日期：`20260412`
- 週期：`n473`
- 班別：`b0023`

已驗證的存檔狀態：

- `sec = b0023`
- `kd = 1`
- `short = 基金會常日班`

## 已驗證範例：2026-04-13 李冠葦 + 陳淑錡

目標：

- `李冠葦(101)` -> `0000000005`
- `陳淑錡(102)` -> `0000000001`
- 日期：`20260413`
- 週期：`n473`
- 班別：`b0023`

兩位都是在完成以下步驟後才成功存檔：

1. 員工 A -> 套用 -> 存檔 -> 重新整理 -> 驗證
2. 員工 B -> 套用 -> 存檔 -> 重新整理 -> 驗證

## 跳窗處理

存檔後系統可能會顯示：

- 警告視窗
- 成功視窗
- 兩者都有

一律嘗試：

```python
for label in ("確定", "OK"):
    button = page.get_by_role("button", name=label)
    if await button.count():
        await button.first.click()
        await page.wait_for_timeout(1200)
```

## 驗證標準

只有來自重新整理後的頁面狀態，驗證才算有效：

```javascript
const target = row.DaysInfo.find(d => d.date === targetDate);
return {
  sec: target.sec,
  kd: target.kd,
  hdsec: target.HdSec,
  short: target.NameShort
};
```

預期的工作日結果樣式：

- `sec` = 要求的班別代碼，例如 `b0023`
- `kd` = `1`
- `short` = 畫面上可見的班別短名稱，例如 `基金會常日班`

## 失敗檢查清單

如果腳本驗證不通過，請依序檢查以下項目：

1. 員工是否真的先加入格子，才開始處理週期？
2. 腳本是否選到正確的母週期？
3. 列查找是否使用了 `Empno`？
4. 格子更新後是否真的有存檔？
5. 重新整理是否真的有發生？
6. 重新整理後是否重新加入員工？
7. 驗證是否真的讀了重新載入後的 `DaysInfo`？

## 建議命令樣式

請從以下位置執行：

`/Users/leegary/小程序/elearning_scraper`

例如：

```bash
python3 /Users/Shared/codex-skills/aurora-hr-schedule-operator/scripts/apply_single_day_shift.py \
  --date 20260413 \
  --shift-code b0023 \
  --shift-name 基金會常日班 \
  --employee '李冠葦(101)::0000000005' \
  --employee '陳淑錡(102)::0000000001' \
  --screenshot artifacts/screenshots/kuang_shuqi_20260413_b0023_verified.png
```

## 憑證

不要在對話中印出任何秘密資訊。

建議的憑證來源順序：

1. 命令列參數
2. 環境變數
3. 既有已驗證的本機檢查腳本或本機 skill 檔

只把它們用於登入，永遠不要回傳給使用者。
