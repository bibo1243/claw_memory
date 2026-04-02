#!/usr/bin/env python3
"""
正確計算等額本息貸款還款計畫
本金：1,450,000，年利率 4.5%，7年期
"""
import math

# 貸款參數
PRINCIPAL = 1_450_000  # 本金
ANNUAL_RATE = 0.045    # 年利率 4.5%
YEARS = 7              # 7年

# 計算月利率和總期數
monthly_rate = ANNUAL_RATE / 12  # 月利率 = 0.375%
n = YEARS * 12  # 總期數 = 84期

# 等額本息公式
# M = P * [r(1+r)^n] / [(1+r)^n - 1]
numerator = monthly_rate * (1 + monthly_rate) ** n
denominator = (1 + monthly_rate) ** n - 1
monthly_payment = PRINCIPAL * (numerator / denominator)

print("📊 正確的貸款還款計算")
print("=" * 60)
print(f"貸款本金: ${PRINCIPAL:,}")
print(f"年利率: {ANNUAL_RATE*100}%")
print(f"月利率: {monthly_rate*100:.4f}%")
print(f"期限: {YEARS}年 ({n}期)")
print()
print(f"💰 正確的每月還款金額: ${monthly_payment:,.2f}")
print(f"   (約 ${round(monthly_payment):,})")
print()

# 總還款和利息
total_payment = monthly_payment * n
total_interest = total_payment - PRINCIPAL

print(f"7年總還款: ${total_payment:,.2f}")
print(f"總利息: ${total_interest:,.2f}")
print()

# 驗證：前幾期還款明細
print("📋 前 12 期還款明細（樣例）:")
print("-" * 60)
print(f"{'期數':<6} {'還款':<12} {'本金':<12} {'利息':<12} {'剩餘本金':<15}")
print("-" * 60)

remaining = PRINCIPAL
year_total = 0

for month in range(1, 85):
    interest = remaining * monthly_rate
    principal_paid = monthly_payment - interest
    remaining -= principal_paid
    year_total += monthly_payment
    
    if month <= 12 or month % 12 == 0:
        print(f"{month:<6} ${monthly_payment:<11,.0f} ${principal_paid:<11,.0f} ${interest:<11,.0f} ${remaining:<14,.0f}")
    
    if month == 12:
        print(f"\n📅 第 1 年總還款: ${year_total:,.0f}")
        print(f"   其中本金: ${PRINCIPAL - remaining:,.0f}")
        print(f"   其中利息: ${year_total - (PRINCIPAL - remaining):,.0f}")
        print()
        print("... （中間省略）...")
        print()
    
    if remaining < 0:
        remaining = 0

print()
print("=" * 60)
print()
print("💡 與你原本的估計比較:")
print(f"  你原本估計: $25,000/月")
print(f"  正確計算:   ${monthly_payment:,.0f}/月")
diff = 25000 - monthly_payment
if diff > 0:
    print(f"  差額:       你多估了 ${diff:,.0f}/月")
else:
    print(f"  差額:       你少估了 ${abs(diff):,.0f}/月")
print()
print("📊 對每月預算的影響:")
if diff > 0:
    print(f"  每月可多出: ${diff:,.0f}")
else:
    print(f"  每月需補足: ${abs(diff):,.0f}")
