#!/usr/bin/env python3
"""
預算管理系統 - Gary 最終版 v3
包含給媽媽的孝親費
"""
import requests
import json
import datetime

NOTION_TOKEN = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
TRANSACTIONS_DB_ID = "30a1fbf9-30df-81fa-91a1-d3e62216ac10"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Gary 的最終版每月預算 v3（2026-04-03 更新）
# 新增：給媽媽 $15,000/月
DEFAULT_BUDGET = {
    # 固定必要支出 ($23,500)
    "電話費": 2000,
    "網路及AI服務": 4000,
    "行 (交通)": 2500,
    "給媽媽": 15000,
    
    # 生活變動支出 ($15,000)
    "食 (三餐/飲料)": 6000,
    "Food (聚餐)": 1000,
    "Food": 1000,
    "衣 (服飾)": 2000,
    "生活用品": 1000,
    "學習/娛樂": 3000,
    "雜支": 2000,
    
    # 儲蓄與緊急預備 ($11,649)
    "緊急預備金": 6989,
    "額外儲蓄": 4660,
    
    # 貸款還款（固定）($24,905)
    "白銀貸款還款": 24905,
}

def get_monthly_expenses(year=None, month=None):
    """取得指定月份的支出"""
    if year is None:
        year = datetime.datetime.now().year
    if month is None:
        month = datetime.datetime.now().month
    
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    url = f"https://api.notion.com/v1/databases/{TRANSACTIONS_DB_ID}/query"
    
    payload = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"on_or_after": start_date}},
                {"property": "Date", "date": {"before": end_date}}
            ]
        },
        "page_size": 100
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        
        category_totals = {}
        total = 0
        
        for item in results:
            props = item.get("properties", {})
            amount = props.get("Amount", {}).get("number", 0) or 0
            
            category_prop = props.get("Category", {})
            category = ""
            if category_prop and category_prop.get("select"):
                category = category_prop["select"].get("name", "未分類")
            
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount
            total += amount
        
        return category_totals, total, len(results)
    
    return {}, 0, 0

def show_budget_report():
    """顯示預算報表"""
    now = datetime.datetime.now()
    
    print(f"📊 {now.year}年{now.month}月 預算報告")
    print("=" * 60)
    
    expenses, total_expense, count = get_monthly_expenses()
    
    print(f"\n💰 總支出: ${total_expense:,.0f} ({count} 筆)\n")
    
    print("📂 分類明細:")
    print("-" * 60)
    print(f"{'分類':<20} {'預算':>10} {'已用':>10} {'剩餘':>10} {'%':>6}")
    print("-" * 60)
    
    total_budget = 0
    total_remaining = 0
    
    categories = {
        "🍽️ 餐飲": ["食 (三餐/飲料)", "Food (聚餐)", "Food", "點心宵夜"],
        "📱 固定": ["電話費", "網路及AI服務", "行 (交通)", "給媽媽"],
        "👔 生活": ["衣 (服飾)", "生活用品", "學習/娛樂", "雜支"],
        "💎 儲蓄": ["緊急預備金", "額外儲蓄"],
        "💳 貸款": ["白銀貸款還款"],
    }
    
    for cat_name, items in categories.items():
        cat_budget = sum([DEFAULT_BUDGET.get(item, 0) for item in items])
        cat_spent = sum([expenses.get(item, 0) for item in items])
        cat_remaining = cat_budget - cat_spent
        pct = (cat_spent / cat_budget * 100) if cat_budget > 0 else 0
        
        if cat_budget > 0:
            status = "✅" if cat_remaining >= 0 else "⚠️"
            print(f"{status} {cat_name:<18} ${cat_budget:>8,} ${cat_spent:>8,.0f} ${cat_remaining:>8,.0f} {pct:>5.0f}%")
            
            for item in items:
                budget = DEFAULT_BUDGET.get(item, 0)
                if budget > 0:
                    spent = expenses.get(item, 0)
                    print(f"    {item:<16} ${budget:>8,} ${spent:>8,.0f}")
            
            total_budget += cat_budget
            total_remaining += cat_remaining
    
    print("-" * 60)
    print(f"{'總計':<20} ${total_budget:>8,} ${total_expense:>8,.0f} ${total_remaining:>8,.0f}")
    
    other_expenses = {k: v for k, v in expenses.items() if k not in DEFAULT_BUDGET}
    if other_expenses:
        print(f"\n📌 其他支出（無預算）:")
        for cat, amount in other_expenses.items():
            print(f"   {cat}: ${amount:,.0f}")
    
    print("\n" + "=" * 60)
    
    print("\n💡 預算建議:")
    
    # 檢查餐飲
    food_budget = DEFAULT_BUDGET.get("食 (三餐/飲料)", 6000)
    food_spent = expenses.get("食 (三餐/飲料)", 0) + expenses.get("Food", 0) + expenses.get("Food (聚餐)", 0)
    food_pct = food_spent / food_budget * 100 if food_budget > 0 else 0
    
    if food_pct > 80:
        print(f"   ⚠️  餐飲已用 {food_pct:.0f}%，注意控制每日 $200 上限！")
    elif food_pct > 50:
        print(f"   ⚡ 餐飲已用 {food_pct:.0f}%，還算可控")
    else:
        print(f"   ✅ 餐飲控制良好")
    
    # 檢查給媽媽
    mom_budget = DEFAULT_BUDGET.get("給媽媽", 15000)
    mom_spent = expenses.get("給媽媽", 0)
    if mom_spent >= mom_budget:
        print(f"   ✅ 已給媽媽 ${mom_spent:,.0f}")
    elif mom_spent > 0:
        print(f"   📌 本月已給媽媽 ${mom_spent:,.0f}，還差 ${mom_budget - mom_spent:,.0f}")
    else:
        print(f"   📌 本月還沒給媽媽 ${mom_budget:,.0f}")
    
    # 整體
    if total_remaining < 0:
        print("   🚨 本月已超支！建議控制非必要支出")
    elif total_remaining < total_budget * 0.1:
        print("   ⚡ 預算剩餘不足 10%，請注意支出")
    else:
        print("   ✅ 預算控制良好，繼續保持！")

if __name__ == "__main__":
    show_budget_report()
