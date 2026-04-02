#!/usr/bin/env python3
"""
Aurora HR 排班作業 - 批次設定多個員工多個日期

使用方式:
    python template_multi_shifts.py --shifts "李冠葦:0000000005:20260414:b0013,陳淑錡:0000000001:20260417:b0006"

參數格式 (--shifts):
    "員工姓名:empno:日期(YYYYMMDD):班別代碼,..."
"""

import argparse
import asyncio
from playwright.async_api import async_playwright
from dataclasses import dataclass

LOGIN_URL = "https://erp6.aoacloud.com.tw/Default.aspx"
PAGE_URL = "https://erp6.aoacloud.com.tw/HR/HRHB007S00.aspx"
COMPANY_ID = "ih5667"
USERNAME = "bibo1243"
PASSWORD = "A128015564"


@dataclass
class ShiftTask:
    name: str
    empno: str
    date: str
    shift_code: str


def parse_args():
    parser = argparse.ArgumentParser(description="Aurora HR 批次排班作業")
    parser.add_argument("--shifts", required=True, help="班別設定（格式：姓名:empno:日期:班別代碼）")
    parser.add_argument("--department", default="行政組", help="部門名稱")
    parser.add_argument("--headful", action="store_true", default=True, help="顯示瀏覽器")
    return parser.parse_args()


def parse_shifts(shifts_str: str) -> list[ShiftTask]:
    tasks = []
    for item in shifts_str.split(','):
        parts = item.strip().split(':')
        if len(parts) != 4:
            print(f"⚠️  格式錯誤: {item}，略過")
            continue
        name, empno, date, shift_code = parts
        tasks.append(ShiftTask(name=name.strip(), empno=empno.strip(), date=date.strip(), shift_code=shift_code.strip()))
    return tasks


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


async def add_employees(page, tasks: list[ShiftTask]):
    empnos = list(dict.fromkeys(t.empno for t in tasks))
    
    print(f"加入員工: {empnos}...")
    for empno in empnos:
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
        await asyncio.sleep(3)
    
    print("✅ 所有員工已加入")


async def set_shift(page, empno: str, date_ymd: str, shift_code: str) -> dict:
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
    await page.evaluate("""() => {
        var btns = document.querySelectorAll('input[type="button"]');
        for (var btn of btns) { if (btn.value === '存檔') { btn.click(); return 'clicked'; } }
    }""")
    await asyncio.sleep(5)


async def main():
    args = parse_args()
    tasks = parse_shifts(args.shifts)
    
    if not tasks:
        print("❌ 沒有有效的班別設定")
        return
    
    print(f"\n共 {len(tasks)} 個班別設定:")
    for t in tasks:
        print(f"  - {t.name} ({t.empno}): {t.date} → {t.shift_code}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.headful)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        await login_and_navigate(page)
        await select_department(page, args.department)
        await add_employees(page, tasks)
        
        for i, task in enumerate(tasks):
            print(f"\n[{i+1}/{len(tasks)}] 設定 {task.name} {task.date} → {task.shift_code}")
            result = await set_shift(page, task.empno, task.date, task.shift_code)
            
            if result.get('error'):
                print(f"  ❌ 錯誤: {result['error']}")
            else:
                print(f"  ✅ {result['name']} {result['date']} → {result['shiftName']} ({result['shiftCode']})")
        
        await save(page)
        print("\n🎉 完成!")
        
        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
