#!/usr/bin/env python3
"""
Gary 的白銀投資盤點
計算目前的持倉和成本
"""

# 匯率（假設 1 USD = 32 TWD）
USD_TO_TWD = 32

# 白銀持倉
SILVER_HOLDINGS = {
    "10盎司銀條": {"quantity": 3, "unit_oz": 10},
    "1盎司楓葉幣": {"quantity": 106, "unit_oz": 1},
    "1公斤白銀": {"quantity": 32, "unit_oz": 32.1507}  # 1公斤 = 32.1507盎司
}

# 買入資訊
BUY_PRICE_USD = 36  # 美元/盎司
BUY_PRICE_TWD = BUY_PRICE_USD * USD_TO_TWD  # 台幣/盎司

# 貸款資訊
LOAN_1 = 1_140_000
LOAN_2 = 650_000
TOTAL_LOAN = LOAN_1 + LOAN_2

print("🥈 Gary 的白銀投資盤點")
print("=" * 60)
print()

# 計算總盎司數
total_oz = 0
print("📦 目前持倉:")
print("-" * 60)

for item, data in SILVER_HOLDINGS.items():
    oz = data["quantity"] * data["unit_oz"]
    total_oz += oz
    print(f"  {item}: {data['quantity']} × {data['unit_oz']} oz = {oz:,.1f} oz")

print("-" * 60)
print(f"  總計: {total_oz:,.1f} 盎司")
print()

# 計算成本
total_cost_usd = total_oz * BUY_PRICE_USD
total_cost_twd = total_oz * BUY_PRICE_TWD

print("💰 投資成本計算:")
print("-" * 60)
print(f"  買入價格: ${BUY_PRICE_USD}/oz = ${BUY_PRICE_TWD:,}/oz")
print(f"  總盎司數: {total_oz:,.1f} oz")
print(f"  總成本: ${total_cost_usd:,.0f} USD")
print(f"         ${total_cost_twd:,.0f} TWD")
print()

# 貸款使用狀況
print("📊 貸款使用狀況:")
print("-" * 60)
print(f"  總借款:     ${TOTAL_LOAN:,}")
print(f"  白銀成本:   ${total_cost_twd:,.0f}")
unused = TOTAL_LOAN - total_cost_twd
if unused > 0:
    print(f"  未使用資金: ${unused:,} ({unused/TOTAL_LOAN*100:.1f}%)")
    print(f"    可能用途: 保險、保管費、手續費、或保留現金")
else:
    print(f"  超支:       ${abs(unused):,}")
    print(f"    可能原因: 實際買入價高於 $36，或其他費用")

print()

# 預估未來價值
print("🔮 未來價值預估:")
print("-" * 60)

target_prices = [50, 100, 200, 300, 500]
for price in target_prices:
    value_usd = total_oz * price
    value_twd = value_usd * USD_TO_TWD
    profit_twd = value_twd - total_cost_twd
    profit_pct = (value_twd / total_cost_twd - 1) * 100
    
    print(f"  若銀價 ${price}/oz:")
    print(f"    價值: ${value_twd:,.0f}")
    print(f"    獲利: ${profit_twd:,.0f} ({profit_pct:.0f}%)")
    print()

# 盈虧平衡點
break_even_price_usd = total_cost_twd / USD_TO_TWD / total_oz
print(f"💡 盈虧平衡點: ${break_even_price_usd:.2f}/oz")
print(f"   （高於此價格開始賺錢）")
print()

# 風險分析
current_market_price = 36  # 假設目前市價
if current_market_price < BUY_PRICE_USD:
    loss_pct = (1 - current_market_price / BUY_PRICE_USD) * 100
    print(f"⚠️  若目前市價 ${current_market_price}:")
    print(f"   帳面虧損約 {loss_pct:.1f}%")
else:
    profit_pct = (current_market_price / BUY_PRICE_USD - 1) * 100
    print(f"✅ 若目前市價 ${current_market_price}:")
    print(f"   帳面獲利約 {profit_pct:.1f}%")

print()
print("=" * 60)
print("🎯 總結")
print("=" * 60)
print(f"你持有 {total_oz:,.0f} 盎司白銀")
print(f"成本約 ${total_cost_twd:,.0f}（兩筆貸款總額）")
print(f"每月還款 $24,905，還需約 6 年")
print()
print("若7年後銀價達 $500/oz:")
target_value = total_oz * 500 * USD_TO_TWD
profit = target_value - total_cost_twd
print(f"  你的白銀將價值 ${target_value:,.0f}")
print(f"  淨賺 ${profit:,.0f}")
print(f"  還清貸款後，還剩 ${profit:,.0f}！")
