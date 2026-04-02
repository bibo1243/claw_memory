from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

LOGIN_URL = "https://ih5667-login.aoacloud.com.tw/Home/DeskAuthIndex"
PAGE_URL = "https://erp3.aoacloud.com.tw/HR/HRHB007S00.aspx"

DEFAULT_CREDENTIAL_SOURCES = [
    "/Users/leegary/小程序/elearning_scraper/scripts/inspection/inspect_schedule_page.py",
    "/Users/leegary/.claude/skills/aurora_hr_schedule/SKILL.md",
]


@dataclass
class TargetEmployee:
    label: str
    empno: str

    @property
    def name(self) -> str:
        if "(" in self.label:
            return self.label.split("(", 1)[0].strip()
        return self.label.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a work shift to one or more employees on a single date in Aurora HR.")
    parser.add_argument("--date", required=True, help="Target date in YYYYMMDD format. Always normalize ambiguous month/day input before calling this script.")
    parser.add_argument("--shift-code", required=True, help="Shift code such as b0023.")
    parser.add_argument("--shift-name", default="", help="Optional shift name for reporting only.")
    parser.add_argument(
        "--employee",
        action="append",
        required=True,
        help="Employee in the format '李冠葦(101)::0000000005'. Repeat for multiple employees.",
    )
    parser.add_argument("--cycle", help="Optional explicit cycle code. If omitted, infer from the page dropdown.")
    parser.add_argument("--screenshot", default="artifacts/screenshots/single_day_shift_verified.png")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode.")
    return parser.parse_args()


def normalize_ymd(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 8:
        raise SystemExit(f"Invalid date: {value}")
    return digits


def parse_employee(value: str) -> TargetEmployee:
    if "::" not in value:
        raise SystemExit(f"Invalid --employee value: {value}. Use 'Label::Empno'.")
    label, empno = value.split("::", 1)
    label = label.strip()
    empno = empno.strip()
    if not label or not empno:
        raise SystemExit(f"Invalid --employee value: {value}. Use 'Label::Empno'.")
    return TargetEmployee(label=label, empno=empno)


def extract_assignment(text: str, key: str) -> str | None:
    patterns = [
        rf'{key}\s*=\s*"([^"]+)"',
        rf"{key}\s*=\s*'([^']+)'",
        rf"\*\*{key if key != 'USERNAME' else '主管帳號'}\*\*:\s*`([^`]+)`",
        rf"\*\*{key if key != 'PASSWORD' else '主管密碼'}\*\*:\s*`([^`]+)`",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def load_credentials(args: argparse.Namespace) -> tuple[str, str]:
    username = args.username or os.environ.get("AURORA_HR_USERNAME")
    password = args.password or os.environ.get("AURORA_HR_PASSWORD")
    if username and password:
        return username, password

    for path in DEFAULT_CREDENTIAL_SOURCES:
        candidate = Path(path)
        if not candidate.exists():
            continue
        text = candidate.read_text(encoding="utf-8", errors="ignore")
        username = username or extract_assignment(text, "USERNAME")
        password = password or extract_assignment(text, "PASSWORD")
        if username and password:
            return username, password

    raise SystemExit("Missing credentials. Provide --username/--password or set AURORA_HR_USERNAME/AURORA_HR_PASSWORD.")


async def wait_network_idle(page, timeout: int = 15000) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except PlaywrightTimeoutError:
        pass


async def dismiss_common_modals(page) -> None:
    for label in ("確定", "OK"):
        button = page.get_by_role("button", name=label)
        if await button.count():
            await button.first.click()
            await page.wait_for_timeout(1200)


async def login(page, username: str, password: str) -> None:
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")
    await page.fill("#login_name", username)
    await page.fill("#password", password)
    await page.click("#loginBtn")
    await wait_network_idle(page, timeout=20000)
    await page.wait_for_timeout(2000)


async def open_schedule(page) -> None:
    await page.goto(PAGE_URL, wait_until="domcontentloaded")
    await wait_network_idle(page)
    await page.wait_for_timeout(2000)


async def add_employee_to_grid(page, label: str) -> None:
    await page.select_option("#WorkScheduleOrgCtrl_Emp", label=label)
    await page.wait_for_timeout(800)
    await page.get_by_role("button", name="加入").click()
    await page.wait_for_timeout(2600)


def parse_cycle_text_range(text: str) -> tuple[datetime, datetime] | None:
    if text.startswith("-"):
        return None
    match = re.search(r"(\d{4}/\d{2}/\d{2})~(\d{4}/\d{2}/\d{2})", text)
    if not match:
        return None
    start = datetime.strptime(match.group(1), "%Y/%m/%d")
    end = datetime.strptime(match.group(2), "%Y/%m/%d")
    return start, end


async def infer_cycle(page, target_ymd: str) -> dict[str, str]:
    target_date = datetime.strptime(target_ymd, "%Y%m%d")
    payload = await page.locator("#divSearchEmployee #selChangeUserCycRange").evaluate(
        """(el) => Array.from(el.options).map(o => ({
            value: String(o.value || '').replace(/^string:/, ''),
            text: o.text.trim()
        }))"""
    )
    for option in payload:
        if option["value"] == "month":
            continue
        parsed = parse_cycle_text_range(option["text"])
        if not parsed:
            continue
        start, end = parsed
        if start <= target_date <= end:
            return option
    raise RuntimeError(f"No cycle matched {target_ymd}.")


async def apply_single_day_shift(page, cycle: str, target_ymd: str, shift_code: str, target_empno: str) -> dict[str, object]:
    return await page.evaluate(
        """async ({ cycle, ymd, shiftCode, empno }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const vm = scope.vm;

            vm.query.GroupByCycle = cycle;
            scope._GetTableRow();
            await new Promise(resolve => setTimeout(resolve, 8000));

            const row = vm.TableRowsDetail.find(r => r.Empno === empno);
            if (!row) throw new Error('target row not found');

            const idx = row.DaysInfo.findIndex(d => d.date === ymd);
            if (idx < 0) throw new Error('target date not found in cycle');

            vm.controller.HoliDayClass = true;
            vm.controller.SelDutyClass = shiftCode;
            vm.controller.SelAll = false;
            vm.controller.SelHoliDayClass = '4';
            vm.controller.SelHoliDayDutyClass = 'default';
            vm.controller.SelLeaveClass = '';
            vm.chkDutyClass = true;
            vm.chkPstn = false;
            vm.chkNotes = false;
            vm.chkCostDpt = false;
            vm.chkPlace = false;
            vm.chkWorkHoliDay = false;
            vm.HoliDayClassType = '0';

            const cell = row.DaysInfo[idx];
            scope._SetClass(cell, row.DaysInfo, idx, row.EmpnoName || row.Name, row);
            await new Promise(resolve => setTimeout(resolve, 2500));

            const target = row.DaysInfo[idx];
            return {
                row: row.EmpnoName || row.Name,
                target: {
                    date: target.date,
                    sec: target.sec,
                    kd: target.kd,
                    hdsec: target.HdSec,
                    short: target.NameShort
                }
            };
        }""",
        {"cycle": cycle, "ymd": target_ymd, "shiftCode": shift_code, "empno": target_empno},
    )


async def verify_single_day_shift(page, cycle: str, target_ymd: str, target_empno: str) -> dict[str, object]:
    return await page.evaluate(
        """async ({ cycle, ymd, empno }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const vm = scope.vm;

            vm.query.GroupByCycle = cycle;
            scope._GetTableRow();
            await new Promise(resolve => setTimeout(resolve, 8000));

            const row = vm.TableRowsDetail.find(r => r.Empno === empno);
            if (!row) throw new Error('target row not found after reload');
            const target = row.DaysInfo.find(d => d.date === ymd);
            if (!target) throw new Error('target date missing after reload');

            return {
                row: row.EmpnoName || row.Name,
                target: {
                    date: target.date,
                    sec: target.sec,
                    kd: target.kd,
                    hdsec: target.HdSec,
                    short: target.NameShort
                }
            };
        }""",
        {"cycle": cycle, "ymd": target_ymd, "empno": target_empno},
    )


async def save_page(page) -> None:
    await page.click("#btnSave")
    await page.wait_for_timeout(2500)
    await dismiss_common_modals(page)


async def main() -> None:
    args = parse_args()
    username, password = load_credentials(args)
    target_ymd = normalize_ymd(args.date)
    employees = [parse_employee(item) for item in args.employee]
    screenshot_path = Path(args.screenshot)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    # Keep the resolved operation explicit so multi-date requests do not leak the
    # previous date into the next run.
    execution_plan = {
        "date": target_ymd,
        "shift_code": args.shift_code,
        "shift_name": args.shift_name,
        "employees": [{"label": employee.label, "empno": employee.empno} for employee in employees],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.headful)
        ctx = await browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1800, "height": 2400},
            locale="zh-TW",
        )
        page = await ctx.new_page()
        page.set_default_timeout(30000)
        save_responses: list[dict[str, object]] = []

        async def capture_save_response(response) -> None:
            if any(key in response.url for key in ("WorkScheduleRemarks/Save", "WorkScheduleMulti/Save", "SaveWorkCalendar")):
                try:
                    body = await response.text()
                except Exception as exc:
                    body = f"<body error: {exc}>"
                save_responses.append({"url": response.url, "status": response.status, "body": body})

        page.on("response", lambda response: asyncio.create_task(capture_save_response(response)))

        await login(page, username, password)
        await open_schedule(page)

        results: list[dict[str, object]] = []
        inferred_cycle: dict[str, str] | None = None

        for employee in employees:
            await add_employee_to_grid(page, employee.label)
            if args.cycle:
                cycle_code = args.cycle
                cycle_text = args.cycle
            else:
                inferred_cycle = inferred_cycle or await infer_cycle(page, target_ymd)
                cycle_code = inferred_cycle["value"]
                cycle_text = inferred_cycle["text"]

            applied = await apply_single_day_shift(page, cycle_code, target_ymd, args.shift_code, employee.empno)
            await save_page(page)

            await page.reload(wait_until="domcontentloaded")
            await wait_network_idle(page)
            await page.wait_for_timeout(1800)
            await add_employee_to_grid(page, employee.label)
            verified = await verify_single_day_shift(page, cycle_code, target_ymd, employee.empno)

            results.append(
                {
                    "employee": employee.name,
                    "label": employee.label,
                    "empno": employee.empno,
                    "date": target_ymd,
                    "cycle": {"code": cycle_code, "text": cycle_text},
                    "shift": {"code": args.shift_code, "name": args.shift_name},
                    "applied": applied,
                    "verified": verified,
                }
            )

            await open_schedule(page)

        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(
            json.dumps(
                {
                    "execution_plan": execution_plan,
                    "results": results,
                    "save_responses": save_responses,
                    "screenshot": str(screenshot_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
