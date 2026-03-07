#!/usr/bin/env python3
"""Rebuild Notion GTD page using urllib (no requests)."""

import json
import urllib.request
import urllib.error
import time
import sys

NOTION_TOKEN = "ntn_l85223794876RnsslSGi5YK6ZoE90txlq0j1gOmddwc8hR"
PAGE_ID = "30d1fbf9-30df-81bb-9dc5-d6a2418dc5f3"
BASE = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def api(method, path, body=None, raise_on_error=True):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"HTTP {e.code} on {method} {path}: {err_body}", file=sys.stderr, flush=True)
        if raise_on_error:
            raise
        return None

# -- helpers --
def rich(text):
    return [{"type": "text", "text": {"content": text}}]

def heading1(text):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": rich(text)}}

def heading2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich(text)}}

def heading3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": rich(text)}}

def paragraph(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich(text)}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def todo(text, checked=False):
    return {"object": "block", "type": "to_do", "to_do": {"rich_text": rich(text), "checked": checked}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich(text)}}

# ============================================================
# Step 1: Delete existing blocks
# ============================================================
print("=== Step 1: Fetching and deleting existing blocks ===", flush=True)
all_block_ids = []
cursor = None
while True:
    path = f"/blocks/{PAGE_ID}/children?page_size=100"
    if cursor:
        path += f"&start_cursor={cursor}"
    resp = api("GET", path)
    for b in resp.get("results", []):
        all_block_ids.append(b["id"])
    if resp.get("has_more"):
        cursor = resp["next_cursor"]
    else:
        break

print(f"Found {len(all_block_ids)} blocks to delete.", flush=True)

deleted = 0
skipped = 0
for i, bid in enumerate(all_block_ids):
    result = api("DELETE", f"/blocks/{bid}", raise_on_error=False)
    if result is not None:
        deleted += 1
    else:
        skipped += 1
    if (i + 1) % 20 == 0:
        print(f"  Progress: {i+1}/{len(all_block_ids)} (deleted={deleted}, skipped={skipped})", flush=True)
        time.sleep(0.5)  # rate limit
    else:
        time.sleep(0.15)

print(f"Delete phase done: {deleted} deleted, {skipped} skipped (archived/errors).", flush=True)

# ============================================================
# Step 2: Append new content in batches
# ============================================================

batch1 = [
    heading1("🧠 GTD 大腦掃除 — 近一個月任務規劃"),
    paragraph("收集日期：2026-02-20 | 狀態：收集中 (Capture Phase)"),
    divider(),
    heading2("🛒 第一層：個人與健康"),
    heading3("購物清單"),
    todo("購買休閒上衣 (補充斷捨離後的空缺)"),
    todo("鞋子補色"),
    todo("研究電子紙螢幕的小型安卓手機 (護眼用)"),
    todo("購買並佈置家裡植栽"),
    heading3("身體修復"),
    todo("預約整脊與溫灸 (需先確認存錢狀況)"),
    todo("預約牙醫修補牙齒 (優先級高，避免惡化)"),
    todo("剪頭髮 (過年後行程)"),
    heading3("運動打卡"),
    todo("每日晨間運動 06:30-07:30 (建立打卡機制)"),
    divider(),
    heading2("💼 第二層：工作與專案"),
    heading3("第 1 類：急迫死線 (Deadlines)"),
    todo("完成蔡小姐捐贈的處理"),
    todo("準備組織發展會議議題"),
    todo("蓮友慈益基金會兩間房子問題處理"),
    todo("員工旅遊處理"),
    todo("追蹤人資系統進度"),
    todo("發佈年度行事曆"),
    todo("關注勞動檢查結果並因應"),
    todo("籌劃 3 月份佈達「員工宿舍管理辦法」 @慈光核心主管會議"),
    todo("準備 2/26 慈光核心主管會議議題 @慈光核心主管會議"),
    todo("在慈光核心主管會議中提出：與羅叔談退休的事 @慈光核心主管會議"),
    todo("在慈光核心主管會議中討論：董事會時間 @慈光核心主管會議"),
    todo("聯絡董事們開董事會 @董事會 @電話"),
    todo("準備 4 月份董事會主題 @董事會"),
    heading3("第 2 類：團隊與人 (People)"),
    todo("查看衛生準備內容 (與淑錡討論前置)"),
    todo("與淑錡討論人資系統進度"),
    todo("建構倉庫整理系統 (授權紀騰執行，需先建系統)"),
    todo("持續培養其他夥伴（主管核心職責）@與淑錡討論"),
    heading3("第 3 類：會議與培育 (Meetings)"),
    todo("規劃資深團隊行政組培育計畫"),
    todo("安排與有才華夥伴的談話 (培育)"),
    heading3("第 4 類：組織發展 (Big Picture)"),
    todo("構思機構資訊系統開發 (運用自動化技能)"),
    todo("設計組織例行事項管理系統"),
    todo("建立各單位工作狀態掌控機制 — 後退一個高度檢視組織"),
    heading3("第 5 類：承諾與溝通"),
    todo("歸還詹常董宜珮父親的奠儀 @外出"),
    todo("完成主管支持團體的記錄（需找休假時間）@休假時"),
]

batch2 = [
    heading3("第 6 類：管理 (Management)"),
    todo("修繕線上申請系統 SOP — 跟兒家、少家約時間討論流程 @與兒家少家約時間"),
    todo("人事員工工作規則更新 @組織發展會議"),
    todo("機構團保確認 @與鳳翎討論"),
    todo("行政組員工訓練安排＋勞檢/檢舉對話團體＋持續培養夥伴（事前先找顗帆所長邀請協助）@組織發展會議 @與顗帆討論"),
    heading3("第 7 類：人事 (Personnel)"),
    todo("庶務、社資組積極招募 @電腦前"),
    todo("幾位夥伴評估是否升資深 @資深團隊會議"),
    todo("庶務—銘澤，需要跟他聊聊 @與銘澤討論"),
    todo("人事資料卡＋員工工作契約書重新更新 @與鳳翎討論"),
    todo("回覆梅芳特休天數 @與梅芳討論"),
    todo("與梅芳、鳳翎及基金會人員開會討論人事系統上線 @與梅芳討論 @與鳳翎討論"),
    heading3("第 8 類：業務 (Operations)"),
    todo("查看最近社會局是否有聯繫會報 @電腦前"),
    todo("年後與勞工局的小姐確認是否有收到信 @電話"),
    todo("每日完成工作日誌，用 Agent 產出 Word 檔 @電腦前（每日例行）"),
    todo("每週寄出週報告 @電腦前（每週例行）"),
    todo("每小時記錄自己業務執行狀況（AI 輔助）@電腦前（持續例行）"),
    heading3("第 9 類：系統 (Systems)"),
    todo("行事曆系統推動 — 請大家開始操作＋進行教學 @組織發展會議"),
    todo("培養 AI 人才（元鼎、廷瑋、鳳翎、港博、銘澤）— 統一開課？ @組織發展會議"),
    todo("建立行政組工作記錄系統 — 員工丟任務，自動記錄時間/地點/內容/進度/備註/協作者 @電腦前"),
    todo("麗娟公文系統全面改善 @與麗娟討論"),
    todo("員工手冊系統全面改善 @與梅芳討論"),
    todo("梅芳 email 中提到要更新的各種辦法 — 找出哪幾篇待定稿 @組織發展會議"),
    todo("麗娟規劃用 AI 輔助整理文書業務報告 @與麗娟討論"),
    todo("將以前 Notion 工作日誌資料庫分享給 Agent 系統 @電腦前"),
    todo("辦公室需要螢幕＋二樓辦公室安排大掃除 @電腦前 @行政組會議"),
    todo("追蹤元鼎少家網路重拉線進度 @與元鼎討論"),
    heading3("第 10 類：辦公室/場地 (Office/Venue)"),
    todo("跟兩家園主管、淑錡約時間討論衛生稽查分工 @組織發展會議"),
    todo("防災部份全面檢視 @電腦前"),
    todo("兒家保全系統啟動運作 @與兒家少家約時間"),
    todo("年底市長大選 — 少家場地借給區公所作為投開票場地 @行政組會議"),
]

batch3 = [
    divider(),
    heading2("🏷️ Context（場合）標籤系統"),
    paragraph("GTD 的 Context 概念：每個任務標記「在什麼場合下處理」，開會時可快速篩選出該會議要提的議題。"),
    heading3("建議標籤清單"),
    bullet("📋 @慈光核心主管會議 — 需在核心主管會議提出的議題"),
    bullet("📋 @組織發展會議 — 組織大方向及行政的議題"),
    bullet("📋 @董事會 — 需在董事會提出的議題"),
    bullet("📋 @行政組會議 — 需在行政組內部會議討論的"),
    bullet("📋 @資深團隊會議 — 需在資深團隊會議提出的"),
    bullet("📋 @與淑錡討論 — 需跟副組長一對一討論的"),
    bullet("📋 @電腦前 — 需要在電腦前處理的"),
    bullet("📋 @外出時 — 需要外出時順便處理的"),
    bullet("📋 @電話 — 需要打電話處理的"),
    bullet("📋 @休假時 — 需要在休假時處理的"),
    bullet("📋 @與鳳翎討論 — 需跟會計/人事討論的"),
    bullet("📋 @與梅芳討論 — 需跟梅芳討論的"),
    bullet("📋 @與麗娟討論 — 需跟文書麗娟討論的"),
    bullet("📋 @與元鼎討論 — 需跟元鼎討論的"),
    bullet("📋 @與銘澤討論 — 需跟銘澤討論的"),
    bullet("📋 @與顗帆討論 — 需跟顗帆所長討論的"),
    bullet("📋 @與兒家少家約時間 — 需跟家園約時間的"),
    divider(),
    heading2("🔄 第三層：深度收集觸發清單"),
    paragraph("以下根據 GTD「未完成事物觸發清單」展開，結合 Gary 的角色（總幹事 / 行政組長）與個人目標進行全面掃除。"),
    heading3("💼 職業方面"),
    todo("已開始、尚未完成的專案？"),
    todo("需要開始進行的專案？"),
    todo("評估中的專案？"),
    todo("對董事長/董事們的承諾？"),
    todo("對同事（淑錡、紀騰、慧雯、前柏...）的承諾？"),
    todo("對外部合作單位（社會局、基金會夥伴）的承諾？"),
    todo("要歸還的東西？"),
    todo("待回覆的 LINE 訊息？"),
    todo("待回覆的電子郵件？"),
    todo("需要打的電話？"),
    todo("會議記錄待發送？"),
    todo("報告、評鑑文件？"),
    todo("提案、企畫書？"),
    todo("會議紀錄待編寫或修改？"),
    todo("進展匯報、需追蹤的對話與溝通？"),
    todo("預算審核或調整？"),
    todo("應收帳款、應付帳款？"),
    todo("捐贈款處理（如蔡小姐捐贈）？"),
    todo("短/中/長期目標需更新？"),
    todo("即將進行的活動、會議、演講？"),
    todo("年度行事曆待發佈？"),
    todo("架設新系統/設備？"),
    todo("出差、旅行安排？"),
    todo("組織架構圖需更新？"),
    todo("職權關係釐清？"),
    todo("新系統導入？"),
    todo("文化建設、團隊士氣？"),
    todo("法務？"),
    todo("保險？"),
    todo("人事、人員配置？"),
    todo("政策/流程待更新？"),
    todo("招聘、考核、升遷？"),
    todo("員工發展、薪資、回饋？"),
    todo("員工旅遊安排？"),
    todo("近期會議議程準備？"),
    todo("被要求參加的會議？"),
    todo("需簡報的內容？"),
    todo("董事會（需提前通知董事）？"),
    todo("空間擺設、設備維護？"),
    todo("倉庫整理？"),
    todo("衛生檢查準備？"),
    todo("委派他人的事項/專案進度？"),
    todo("對溝通/建議的回覆？"),
    todo("他人的決策/回覆？"),
    todo("報銷、票據？"),
]

batch4 = [
    heading3("🧘 個人方面"),
    todo("對家人（父母）的承諾？"),
    todo("對朋友的承諾？"),
    todo("要歸還的東西、債務？"),
    todo("待回覆的私人訊息？"),
    todo("感謝信、卡片、問候？"),
    todo("社群媒體貼文？"),
    todo("生日、紀念日？"),
    todo("聚會、派對、訪客？"),
    todo("旅行計畫？"),
    todo("文化活動、體育活動？"),
    todo("帳單、銀行事務？"),
    todo("投資、貸款、稅務？"),
    todo("預算規劃、記帳習慣？"),
    todo("保險？"),
    todo("存錢目標設定？"),
    todo("居家維修、整修？"),
    todo("家電、設備、電子產品？"),
    todo("收納、整理、斷捨離？"),
    todo("水電、網路、電信？"),
    todo("清潔、打掃？"),
    todo("植栽佈置？"),
    todo("醫生、牙醫預約？"),
    todo("體檢？"),
    todo("視力保健？"),
    todo("飲食調整？"),
    todo("運動習慣建立？"),
    todo("整脊/溫灸？"),
    todo("課程、研討會、培訓？"),
    todo("要讀的書？"),
    todo("藝人模組深化？"),
    todo("自動化技能提升？"),
    todo("創意表達？"),
    todo("戒色進度 — Streak 追蹤？"),
    todo("「依靠清單」是否有在使用？"),
    todo("能量轉移的新管道探索？"),
    todo("身份認同強化？"),
    todo("汽車/機車保養、維修？"),
    todo("通勤安排？"),
    todo("專業服飾補充？"),
    todo("休閒服飾補充？"),
    todo("鞋子維護？"),
    todo("想去的地方、想拜訪的人？"),
    todo("攝影、運動器材？"),
    todo("娛樂、烹飪？"),
    todo("社區參與、公民活動？"),
    todo("人際關係經營？"),
    todo("訂購的產品、維修中的東西？"),
    todo("借出的物品？"),
    todo("他人的回覆？"),
    todo("家人或朋友完成的專案？"),
]

batches = [batch1, batch2, batch3, batch4]
total_blocks = sum(len(b) for b in batches)
print(f"\n=== Step 2: Writing {total_blocks} blocks in {len(batches)} batches ===")

written = 0
for i, batch in enumerate(batches):
    print(f"\nBatch {i+1}/{len(batches)}: {len(batch)} blocks...")
    body = {"children": batch}
    result = api("PATCH", f"/blocks/{PAGE_ID}/children", body)
    written += len(batch)
    print(f"  ✅ Batch {i+1} done. Total written: {written}")
    if i < len(batches) - 1:
        time.sleep(1)

# ============================================================
# Step 3: Verify
# ============================================================
print(f"\n=== Verification ===")
count = 0
cursor = None
while True:
    path = f"/blocks/{PAGE_ID}/children?page_size=100"
    if cursor:
        path += f"&start_cursor={cursor}"
    resp = api("GET", path)
    count += len(resp.get("results", []))
    if resp.get("has_more"):
        cursor = resp["next_cursor"]
    else:
        break

print(f"✅ Final block count on page: {count}")
print(f"✅ Expected: {total_blocks}")
if count == total_blocks:
    print("🎉 PERFECT MATCH! Rebuild complete.")
else:
    print(f"⚠️  Mismatch: got {count}, expected {total_blocks}")
