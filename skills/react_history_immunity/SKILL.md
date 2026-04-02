---
name: React History Immunity (Undo/Redo)
description: 處理 React 嚴格模式與重複渲染事件下的 undo/redo 歷史堆疊「深層免疫」架構原則。
---

# React History Immunity (Undo/Redo)

當我們在 React 中開發自定義的 `Undo/Redo` (歷史紀錄) 系統時，很容易會遇到以下狀況：
1. **React Strict Mode (嚴格模式)**：在開發環境下，React 會故意將 State Updater (狀態更新函式) 執行兩次，以確保這是一個 Pure Function。如果我們在 Updater 裡面去推入 `past` 或 `future` 陣列，會導致相同歷史被重複推入兩次。
2. **事件重疊 (Race Conditions)**：在使用含有 onBlur、onKeyDown、或滑鼠焦點切換的複雜表單或卡片時，常常會瞬間觸發兩次儲存事件，導致歷史堆疊中塞滿了長得一模一樣的狀態碎片。

這會造成前端操作時的非預期行為（例如按了 Undo 沒反應，要連按四五次；或是 Redo 步驟等比級數異常增加）。

### 深層免疫機制 (Deep Immunity Mechanism)

為了解決這個問題，撰寫 `useHistory` 這類系統時必須遵守以下三大原則：

#### 1. 使用 useRef 做為中央保險箱
不要把 `past` 和 `future` 放在由 React State 依賴的上一步狀態邏輯中。將全部歷史 `useRef` 包裝起來，狀態更新只要負責驅動畫面渲染 (`setPresent`) 即可。

```typescript
const history = useRef({
    past: [] as T[],
    present: initial,
    future: [] as T[]
});
const [present, setPresent] = useState<T>(initial);
```

#### 2. 寫入前強制深度比對 (Deep Equality Check)
在任何推入歷史陣列 (`past`) 的行為前，**必須**透過 `JSON.stringify` 或是深層比對庫檢查，若「要存入的內容」與「當前畫面內容」一模一樣，**直接拋棄**不寫入。

```typescript
const isDifferent = JSON.stringify(nxt) !== JSON.stringify(cur);
if (pushHistory && isDifferent) {
    history.current.past = [...history.current.past, cur]; // 或者儲存 custom snapshot
    history.current.future = [];
}
```

#### 3. 雙向穿透的 Undo / Redo 迴圈
即使有了前面的防禦，以防萬一（或因特殊邏輯匯入），歷史陣列中若殘留相同步驟，`undo` 與 `redo` 本身需要自帶過濾能力，遇到一模一樣的狀態要用 `while` 迴圈瞬間穿越，直到找到一個「與當前狀態真正不同的節點」才停下並觸發畫面渲染。

```typescript
// Undo 範例
let prev;
const cur = history.current.present;

// 跳過跟現在一模一樣的歷史廢料
while (history.current.past.length > 0) {
    prev = history.current.past.pop() as T;
    if (JSON.stringify(prev) !== JSON.stringify(cur)) {
        break; // 找到不一樣的了！
    }
    prev = undefined; // 一樣，丟棄，繼續 pop
}

if (prev === undefined) return; // 沒東西可退了
// ...執行對應的替換邏輯...
```

### 總結
這個「深層歷史免疫機制」保證了：
- **按 1 次還原 ＝ 畫面一定有 1 次有效變更。**
- **避免 React Strict Mode 與短平快操作產生的「幽靈歷史堆疊」。**
- 當專案需開發排程、任務管理、畫布編輯器等需要 Undo/Redo 的系統時，預設帶入此機制。
