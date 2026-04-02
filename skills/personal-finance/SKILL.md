---
name: personal-finance
description: 個人財務管理系統 - 記帳、預算追蹤、貸款計算、投資分析
---

# Personal Finance 個人財務管理

完整的個人財務管理技能，包含記帳、預算追蹤、貸款計算、投資分析等功能。

## 功能

### 1. 智能記帳 (smart_expense.py)
- 自動分類支出
- 預算超標警告
- 整合 Notion 資料庫

### 2. 預算報告 (budget_report.py)
- 每月預算執行狀況
- 分類統計
- 超支提醒

### 3. 貸款計算 (loan_calculator.py)
- 等額本息還款計算
- 多筆貸款管理
- 利息成本分析

### 4. 投資分析 (silver_portfolio.py)
- 白銀投資組合追蹤
- 獲利/虧損計算
- 不同價格情境預估

## 安裝

1. 設定環境變數：
```bash
export NOTION_API_KEY="你的_notion_api_key"
export TRANSACTIONS_DB_ID="你的_notion_db_id"
```

2. 執行腳本：
```bash
python3 scripts/smart_expense.py
```

## 預算設定

預設預算分類：
- 固定支出：孝親費、貸款還款、電話費、網路費、交通費
- 變動支出：餐飲、衣著、生活用品、娛樂
- 儲蓄：緊急預備金、額外儲蓄

## 檔案說明

| 檔案 | 功能 |
|------|------|
| smart_expense.py | 智能記帳主程式 |
| budget_report.py | 預算報告產生器 |
| loan_calculator.py | 貸款還款計算機 |
| silver_portfolio.py | 白銀投資分析 |

## 依賴

- Python 3.8+
- requests
- Notion API 存取權限
