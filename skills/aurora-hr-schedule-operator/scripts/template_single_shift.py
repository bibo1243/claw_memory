#!/usr/bin/env python3
"""
Aurora HR 排班作業 - 單次設定單一員工單一日期

使用方式:
    python template_single_shift.py --empno 0000000005 --date 20260414 --shift b0023

參數說明:
    --empno   員工編號（10位數字字串）
    --date    日期（YYYYMMDD 格式，無斜線）
    --shift   班別代碼（例：b0023, b0006, b0024）
"""

import argparse
import asyncio
from playwright.async_api import async_playwright

LOGIN_URL = "https://erp6.aoacloud.com.tw/Default.aspx"
PAGE_URL = "https://erp6.aoacloud.com.tw/HR/HRHB007S00.aspx"
COMPANY_ID = "ih5667"
USERNAME = "bibo1243"
PASSWORD = "A128015564"


def parse_args():
    parser = argparse.ArgumentParser(description="Aurora HR 排班作業")
    parser.add_argument("--empno", required=True, help="員工編號（10位數字）")
    parser.add_argument("--date", required=True, help="日期（YYYYMMDD）")
    parser.add_argument("--shift", required=True, help="班別代碼")
    parser.add_argument("--department", default="行政組", help="部門名稱")
    parser.add_argument("--headful", action="store_true", default=True, help="顯示瀏覽器")
    return parser.parse_args()


async def login_and_navigate(page):
    print("登入...")
    await page.goto(LOGIN_URL)
    await asyncio.sleep(3)
    
    await page.fill("#company_id", COMPANY_ID)
    await page.fill("#login_name", USERNAME)
    await page.fill("#password", PASSWORD)
    await page.click("button:has-text('登入')")
    await asyncio.sleep(5)
    
    print("進入排班作業...")
    await page.goto(PAGE_URL)
    await asyncio.sleep(5)


async def select_department(page, dept_name):
    print(f"選擇部門 ({dept_name})...")
    await page.evaluate(f"""(name) => {{
        var selects = document.querySelectorAll('select');
        for (var sel of selects) {{
            if (sel.id && sel.id.includes('Dpt')) {{
                var opts = sel.querySelectorAll('option');
                for (var opt of opts) {{
                    if (opt.textContent.includes(name)) {{
                        opt.selected = true;
                        sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return 'OK';
                    }}
                }}
            }}
        }}
    }}""", dept_name)
    await asyncio.sleep(2)


async def add_employee(page, empno):
    print(f"加入員工 (empno={empno})...")
    
    await page.evaluate(f"""(empno) => {{
        var selects = document.querySelectorAll('select');
        for (var sel of selects) {{
            if (sel.id && sel.id.includes('Emp')) {{
                var opts = sel.querySelectorAll('option');
                for (var opt of opts) {{
                    if (opt.value === empno || opt.value === 'string:' + empno) {{
                        opt.selected = true;
                        sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return 'OK: ' + opt.textContent;
                    }}
                }}
            }}
        }}
        return 'NOT_FOUND';
    }}""", empno)
    await asyncio.sleep(1)
    
    await page.evaluate("""() => {
        var btns = document.querySelectorAll('input[type="button"]');
        for (var btn of btns) { if (btn.value === '加入') { btn.click(); return 'clicked'; } }
    }""")
    await asyncio.sleep(5)
    print("  已加入排班表")


async def set_shift(page, empno, date_ymd, shift_code):
    print(f"\n設定班別: empno={empno}, date={date_ymd}, shift={shift_code}")
    
    result = await page.evaluate(f"""async () => {{
        const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
        const vm = scope.vm;
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const row = vm.TableRowsDetail.find(r => r.Empno === '{empno}');
        if (!row) return {{ error: '員工 not found: ' + '{empno}' }};
        
        const idx = row.DaysInfo.findIndex(d => d.date === '{date_ymd}');
        if (idx < 0) return {{ error: '日期 not found: ' + '{date_ymd}' }};
        
        vm.controller.SelDutyClass = '{shift_code}';
        vm.controller.SelAll = false;
        vm.chkDutyClass = true;
        vm.chkPstn = false;
        vm.chkNotes = false;
        
        const cell = row.DaysInfo[idx];
        scope._SetClass(cell, row.DaysInfo, idx, row.EmpnoName || row.Name, row);
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        return {{
            success: true,
            empno: row.Empno,
            name: row.EmpnoName || row.Name,
            date: cell.date,
            shiftCode: cell.sec,
            shiftName: cell.NameShort
        }};
    }}""")
    
    return result


async def save(page):
    print("存檔...")
    await page.evaluate("""() => {
        var btns = document.querySelectorAll('input[type="button"]');
        for (var btn of btns) { if (btn.value === '存檔') { btn.click(); return 'clicked'; } }
    }""")
    await asyncio.sleep(5)


async def main():
    args = parse_args()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.headful)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        await login_and_navigate(page)
        await select_department(page, args.department)
        await add_employee(page, args.empno)
        
        result = await set_shift(page, args.empno, args.date, args.shift)
        
        if result.get('error'):
            print(f"\n❌ 錯誤: {result['error']}")
        else:
            print(f"\n✅ 設定成功!")
            print(f"   員工: {result['name']}")
            print(f"   日期: {result['date']}")
            print(f"   班別: {result['shiftName']} ({result['shiftCode']})")
        
        await page.screenshot(
            path="artifacts/screenshots/shift_result.png",
            full_page=True
        )
        
        await save(page)
        print("\n🎉 完成!")
        
        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
