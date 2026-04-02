#!/usr/bin/env python3
"""
智能記帳腳本 v4
功能：自動分類 + 預算警告 + 不清楚時詢問
"""
import requests
import datetime
import sys

NOTION_TOKEN = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
TRANSACTIONS_DB_ID = "30a1fbf9-30df-81fa-91a1-d3e62216ac10"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 預算表
BUDGET = {
    "給媽媽": 15000, "白銀貸款還款": 24905, "電話費": 2000,
    "網路及AI服務": 4000, "行 (交通)": 2500,
    "食 (三餐/飲料)": 6000, "Food (聚餐)": 1000, "Food": 1000,
    "衣 (服飾)": 2000, "生活用品": 1000,
    "學習/娛樂": 3000, "雜支": 2000,
    "緊急預備金": 6989, "額外儲蓄": 4660,
}

# 每日上限
DAILY_LIMIT = 200  # 餐飲每日上限

# 智能分類關鍵字
CLASSIFICATION_KEYWORDS = {
    "食 (三餐/飲料)": ["早餐", "午餐", "晚餐", "便當", "飯", "麵", "麥當勞", "肯德基", "超商", "咖啡", "飲料"],
    "Food (聚餐)": ["聚餐", "請客", "應酬", "火鍋", "燒烤", "餐廳"],
    "行 (交通)": ["加油", "停車", "洗車", "悠遊卡", "公車", "捷運", "計程車", "Uber", "高鐵"],
    "衣 (服飾)": ["衣服", "褲子", "鞋子", "外套", "內衣", "襪子", "Uniqlo", "Zara"],
    "生活用品": ["洗髮", "沐浴", "牙育", "衛生紙", "洗衣", "清潔", "全聯", "康是美", "屈臣氏"],
    "學習/娛樂": ["電影", "遊戲", "KTV", "旅遊", "書", "課程", "Netflix", "Switch", "健身"],
    "電話費": ["電話", "中華電信", "遠傳"],
    "網路及AI服務": ["網路", "WiFi", "Notion", "ChatGPT", "AI"],
    "給媽媽": ["媽媽", "孝親", "家用"],
}

def get_current_spending(category):
    """取得本月目前花費"""
    today = datetime.datetime.now()
    start_date = today.strftime("%Y-%m-01")
    
    url = f"https://api.notion.com/v1/databases/{TRANSACTIONS_DB_ID}/query"
    payload = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"on_or_after": start_date}},
                {"property": "Category", "select": {"equals": category}}
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            total = sum([item["properties"]["Amount"]["number"] or 0 for item in results])
            return total
    except:
        pass
    return 0

def classify_expense(description):
    """智能分類"""
    desc_lower = description.lower()
    
    for category, keywords in CLASSIFICATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    
    return None

def check_budget_warning(category, amount):
    """檢查預算警告"""
    if category not in BUDGET:
        return None
    
    budget_limit = BUDGET[category]
    current_spent = get_current_spending(category)
    remaining = budget_limit - current_spent
    
    # 檢查是否會超支
    if current_spent + amount > budget_limit:
        over = current_spent + amount - budget_limit
        return f"🚨 警告：這筆會讓 '{category}' 超支 ${over:,.0f}！\n   預算：${budget_limit:,} | 已用：${current_spent:,} | 剩餘：${remaining:,}"
    
    # 檢查是否接近上限
    usage_pct = (current_spent + amount) / budget_limit * 100
    if usage_pct >= 90:
        return f"⚠️  注意：'{category}' 已用 {usage_pct:.0f}%，接近上限！"
    elif usage_pct >= 80:
        return f"💡 提醒：'{category}' 已用 {usage_pct:.0f}%，注意控管。"
    
    return None

def add_to_notion(item, amount, category, note=""):
    """新增到 Notion"""
    url = "https://api.notion.com/v1/pages"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "parent": {"database_id": TRANSACTIONS_DB_ID},
        "properties": {
            "Item": {"title": [{"text": {"content": item}}]},
            "Amount": {"number": float(amount)},
            "Date": {"date": {"start": today}},
            "Category": {"select": {"name": category}},
        }
    }
    
    if note:
        payload["properties"]["Note"] = {"rich_text": [{"text": {"content": note}}]}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    return response.status_code == 200

def interactive_mode():
    """互動式記帳"""
    print("📝 智能記帳系統")
    print("=" * 60)
    print()
    print("請輸入支出資訊（格式：項目 金額 說明）")
    print("例如：午餐 120 公司附近的便當店")
    print("或：加油 1500 Shell 95無鉛")
    print()
    
    user_input = input("📌 支出：").strip()
    
    # 解析輸入
    parts = user_input.split()
    if len(parts) < 2:
        print("❌ 格式錯誤！請輸入：項目 金額")
        return
    
    # 解析
    try:
        amount = float(parts[-1])
        description = " ".join(parts[:-1])
    except ValueError:
        # 金額可能在中間
        for i, part in enumerate(parts):
            try:
                amount = float(part)
                description = " ".join(parts[:i] + parts[i+1:])
                break
            except:
                continue
        else:
            print("❌ 找不到金額！請輸入數字。")
            return
    
    print(f"\n📝 你輸入：'{description}' ${amount:,.0f}")
    print()
    
    # 智能分類
    category = classify_expense(description)
    
    if category:
        print(f"✅ 自動分類：'{category}'")
        
        # 檢查預算警告
        warning = check_budget_warning(category, amount)
        if warning:
            print(warning)
            confirm = input("\n⚠️  確定要記這筆嗎？(yes/no): ")
            if confirm.lower() not in ["yes", "y", "是"]:
                print("❌ 已取消")
                return
        
    else:
        print("🤔 無法自動分類，請選擇：")
        print()
        print("【1】食 (三餐/飲料) - 每日上限 $200")
        print("【2】Food (聚餐)")
        print("【3】行 (交通) - 每月上限 $2,500")
        print("【4】衣 (服飾)")
        print("【5】生活用品")
        print("【6】學習/娛樂")
        print("【7】雜支")
        print("【8】其他（我會學習）")
        print()
        
        choice = input("選擇分類 (1-8): ").strip()
        
        category_map = {
            "1": "食 (三餐/飲料)", "2": "Food (聚餐)", "3": "行 (交通)",
            "4": "衣 (服飾)", "5": "生活用品", "6": "學習/娛樂",
            "7": "雜支"
        }
        
        if choice in category_map:
            category = category_map[choice]
            
            # 檢查預算警告
            warning = check_budget_warning(category, amount)
            if warning:
                print(warning)
                confirm = input("\n⚠️  確定要記這筆嗎？(yes/no): ")
                if confirm.lower() not in ["yes", "y", "是"]:
                    print("❌ 已取消")
                    return
        else:
            category = input("請輸入分類名稱：").strip()
    
    # 新增到 Notion
    note = input("\n📝 備註（可選，直接按 Enter 跳過）：").strip()
    
    print()
    print("💾 正在儲存...")
    
    if add_to_notion(description, amount, category, note):
        print(f"✅ 記帳成功！")
        print(f"   項目：{description}")
        print(f"   金額：${amount:,.0f}")
        print(f"   分類：{category}")
        
        # 顯示該分類狀態
        current = get_current_spending(category)
        budget = BUDGET.get(category, 0)
        remaining = budget - current
        print(f"   預算狀態：${current:,.0f} / ${budget:,}（剩餘 ${remaining:,}）")
    else:
        print("❌ 儲存失敗，請檢查 Notion 連線")

if __name__ == "__main__":
    interactive_mode()
