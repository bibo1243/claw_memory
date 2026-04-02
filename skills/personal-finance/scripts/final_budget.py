#!/usr/bin/env python3
"""
Gary 的最終版每月預算
根據最新資訊更新
"""

SALARY = 75_054  # 實領固定收入
LOAN_PAYMENT = 24_905  # 白銀貸款還款

print("💰 Gary 的最終版每月預算")
print("=" * 60)
print()

print("📊 收入與固定支出")
print("-" * 60)
print(f"固定收入:     ${SALARY:,}")
print(f"白銀貸款還款: -${LOAN_PAYMENT:,}")
print(f"剩餘可用:     ${SALARY - LOAN_PAYMENT:,}")
print()

# 固定必要支出
fixed_expenses = {
    "電話費": 2000,
    "網路及AI服務": 4000,
    "交通": 2500,
    "給媽媽": 15000,
}

total_fixed = sum(fixed_expenses.values())

print("📱 固定必要支出")
print("-" * 60)
for item, amount in fixed_expenses.items():
    print(f"  {item}: ${amount:,}")
print(f"  小計: ${total_fixed:,}")
print()

# 生活變動支出
living_expenses = {
    "食（三餐/外食）": 6000,  # 每日 $200
    "Food（聚餐）": 1000,
    "衣/生活用品": 3000,
    "學習/娛樂": 3000,
    "雜支": 2000,
}

total_living = sum(living_expenses.values())

print("🍽️ 生活變動支出")
print("-" * 60)
for item, amount in living_expenses.items():
    print(f"  {item}: ${amount:,}")
print(f"  小計: ${total_living:,}")
print()

# 儲蓄/緊急預備
remaining = SALARY - LOAN_PAYMENT - total_fixed - total_living

print("💎 儲蓄與緊急預備")
print("-" * 60)
print(f"  剩餘可用: ${remaining:,}")
print()

# 建議分配
emergency = min(remaining * 0.6, 15000)  # 緊急預備最多 1.5萬
extra_savings = remaining - emergency

print("💡 建議分配:")
print(f"  緊急預備金:   ${emergency:,.0f}")
print(f"  額外儲蓄:     ${extra_savings:,.0f}")
print()

# 總結
print("=" * 60)
print("📋 預算總覽")
print("=" * 60)
print(f"{'項目':<20} {'金額':<15} {'占比':<10}")
print("-" * 60)

categories = [
    ("白銀貸款還款", LOAN_PAYMENT),
    ("電話/網路/AI", total_fixed),
    ("生活支出", total_living),
    ("緊急預備", emergency),
    ("額外儲蓄", extra_savings),
]

total_allocated = 0
for name, amount in categories:
    pct = amount / SALARY * 100
    print(f"{name:<20} ${amount:<14,.0f} {pct:<9.0f}%")
    total_allocated += amount

print("-" * 60)
print(f"{'總計':<20} ${total_allocated:<14,.0f} 100%")
print()

# 每日提醒
print("📱 每日花費上限提醒")
print("-" * 60)
print(f"  每日餐飲上限: $200")
print(f"  每週娛樂上限: ${living_expenses['學習/娛樂']/4:,.0f}")
print(f"  每月交通上限: ${fixed_expenses['交通']:,}")
print()

print("=" * 60)
print("✅ 預算已設定完成！明天開始記帳！")
print("=" * 60)
