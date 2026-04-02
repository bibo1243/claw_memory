from __future__ import annotations

import argparse
import asyncio
import os
import re
from datetime import datetime, timedelta
from pathlib import Path


LOGIN_URL = "https://ih5667-login.aoacloud.com.tw/Home/DeskAuthIndex"
PAGE_URL = "https://erp3.aoacloud.com.tw/HR/HRHB007S00.aspx"


async def wait_network_idle(page, timeout: int = 15000) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    username = args.username or os.environ.get("AURORA_HR_USERNAME")
    password = args.password or os.environ.get("AURORA_HR_PASSWORD")
    if not username or not password:
        raise SystemExit("Missing credentials. Use --username/--password or AURORA_HR_USERNAME/AURORA_HR_PASSWORD.")
    return username, password


def infer_target_name(target_label: str) -> str:
    if "(" in target_label:
        return target_label.rsplit("(", 1)[0].strip()
    return target_label.strip()


def normalize_ymd(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 8:
        raise SystemExit(f"Invalid date: {value}")
    return digits


def format_ymd(ymd: str) -> str:
    return f"{ymd[:4]}/{ymd[4:6]}/{ymd[6:8]}"


def parse_time_range(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\d{2}:\d{2})-(\d{2}:\d{2})", value.strip())
    if not match:
        raise SystemExit(f"Invalid range: {value}. Use HH:MM-HH:MM.")
    return match.group(1), match.group(2)


def build_date_groups(start_ymd: str, end_ymd: str) -> tuple[list[str], list[str], list[str]]:
    start = datetime.strptime(start_ymd, "%Y%m%d").date()
    end = datetime.strptime(end_ymd, "%Y%m%d").date()
    weekdays: list[str] = []
    saturdays: list[str] = []
    sundays: list[str] = []
    current = start
    while current <= end:
        ymd = current.strftime("%Y%m%d")
        if current.weekday() == 5:
            saturdays.append(ymd)
        elif current.weekday() == 6:
            sundays.append(ymd)
        else:
            weekdays.append(ymd)
        current += timedelta(days=1)
    return weekdays, saturdays, sundays


def sum_range_hours(ranges: list[tuple[str, str]]) -> str:
    total_minutes = 0
    for start, end in ranges:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        total_minutes += int((end_dt - start_dt).total_seconds() // 60)
    hours = total_minutes / 60
    if hours.is_integer():
        return str(int(hours))
    return str(hours)


def summarize_cycle(summary: list[dict[str, str]], start_ymd: str, end_ymd: str, work_sec: str, rest_kd: str, holiday_kd: str) -> dict[str, int]:
    counts = {"work": 0, "rest": 0, "holiday": 0, "other": 0}
    for item in summary:
        if not (start_ymd <= item["date"] <= end_ymd):
            continue
        if item["kd"] == holiday_kd and item["hdsec"] == "":
            counts["holiday"] += 1
        elif item["kd"] == rest_kd and item["hdsec"] == "":
            counts["rest"] += 1
        elif item["sec"] == work_sec and item["kd"] == "1" and item["hdsec"] == "":
            counts["work"] += 1
        else:
            counts["other"] += 1
    return counts


async def login(page, login_url: str, username: str, password: str) -> None:
    await page.goto(login_url, wait_until="domcontentloaded")
    await page.fill("#login_name", username)
    await page.fill("#password", password)
    await page.click("#loginBtn")
    await wait_network_idle(page, timeout=20000)
    await page.wait_for_timeout(1800)


async def open_schedule_page(page, page_url: str) -> None:
    await page.goto(page_url, wait_until="domcontentloaded")
    await wait_network_idle(page)
    await page.wait_for_timeout(1500)


async def add_employee_to_grid(page, target_label: str) -> None:
    await page.select_option("#WorkScheduleOrgCtrl_Emp", label=target_label)
    await page.wait_for_timeout(800)
    await page.get_by_role("button", name="加入").click()
    await page.wait_for_timeout(2200)


async def dismiss_common_modals(page) -> None:
    for label in ("確定", "OK"):
        button = page.get_by_role("button", name=label)
        if await button.count():
            await button.first.click()
            await page.wait_for_timeout(1200)


async def load_cycle(page, cycle: str) -> None:
    await page.evaluate(
        """async ({ cycle }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            scope.vm.query.GroupByCycle = cycle;
            scope._GetTableRow();
            await new Promise(resolve => setTimeout(resolve, 8000));
        }""",
        {"cycle": cycle},
    )


async def save_page(page) -> None:
    await page.click("#btnSave")
    await page.wait_for_timeout(2500)
    await dismiss_common_modals(page)


async def read_cycle_summary(page, target_label: str, target_name: str) -> dict[str, object]:
    return await page.evaluate(
        """({ targetLabel, targetName }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const row = scope.vm.TableRowsDetail.find(r => r.EmpnoName === targetLabel || r.Name === targetName);
            if (!row) throw new Error('target row not found');
            return {
                row: row.EmpnoName || row.Name,
                summary: row.DaysInfo.map(d => ({
                    date: d.date,
                    sec: d.sec,
                    kd: d.kd,
                    hdsec: d.HdSec,
                    short: d.NameShort
                }))
            };
        }""",
        {"targetLabel": target_label, "targetName": target_name},
    )


async def apply_cycle_template(page, args: argparse.Namespace, target_name: str) -> dict[str, object]:
    weekdays, saturdays, sundays = build_date_groups(args.start_date, args.end_date)
    applied = await page.evaluate(
        """async ({ targetLabel, targetName, cycle, workSec, restKd, holidayKd, weekdays, saturdays, sundays }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const vm = scope.vm;

            vm.query.GroupByCycle = cycle;
            scope._GetTableRow();
            await new Promise(resolve => setTimeout(resolve, 8000));

            const row = vm.TableRowsDetail.find(r => r.EmpnoName === targetLabel || r.Name === targetName);
            if (!row) throw new Error('target row not found');

            const configureWork = () => {
                vm.controller.HoliDayClass = true;
                vm.controller.SelDutyClass = workSec;
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
            };

            const configureHoliday = (kd) => {
                vm.controller.HoliDayClass = false;
                vm.controller.SelHoliDayClass = kd;
                vm.controller.SelHoliDayDutyClass = 'default';
                vm.controller.SelLeaveClass = '';
                vm.controller.SelAll = false;
                vm.chkDutyClass = true;
                vm.chkPstn = false;
                vm.chkNotes = false;
                vm.chkCostDpt = false;
                vm.chkPlace = false;
                vm.chkWorkHoliDay = false;
                vm.HoliDayClassType = '0';
            };

            const applyCell = async (ymd, mode, kd) => {
                const idx = row.DaysInfo.findIndex(d => d.date === ymd);
                if (idx < 0) throw new Error('missing day ' + ymd);
                const cell = row.DaysInfo[idx];
                if (mode === 'work') {
                    configureWork();
                } else {
                    configureHoliday(kd);
                }
                scope._SetClass(cell, row.DaysInfo, idx, row.EmpnoName || row.Name, row);
                await new Promise(resolve => setTimeout(resolve, 180));
            };

            for (const ymd of weekdays) await applyCell(ymd, 'work', '1');
            for (const ymd of saturdays) await applyCell(ymd, 'holiday', restKd);
            for (const ymd of sundays) await applyCell(ymd, 'holiday', holidayKd);

            await new Promise(resolve => setTimeout(resolve, 4000));

            return {
                row: row.EmpnoName || row.Name,
                summary: row.DaysInfo.map(d => ({
                    date: d.date,
                    sec: d.sec,
                    kd: d.kd,
                    hdsec: d.HdSec,
                    short: d.NameShort
                }))
            };
        }""",
        {
            "targetLabel": args.target_label,
            "targetName": target_name,
            "cycle": args.cycle,
            "workSec": args.work_sec,
            "restKd": args.rest_kd,
            "holidayKd": args.holiday_kd,
            "weekdays": weekdays,
            "saturdays": saturdays,
            "sundays": sundays,
        },
    )
    return {
        "applied": summarize_cycle(applied["summary"], args.start_date, args.end_date, args.work_sec, args.rest_kd, args.holiday_kd),
        "raw": applied,
    }


async def set_multi_range_day(page, args: argparse.Namespace, target_name: str) -> dict[str, object]:
    ranges = [parse_time_range(item) for item in args.ranges]
    hours_sum = sum_range_hours(ranges)
    result = await page.evaluate(
        """async ({ targetLabel, targetName, cycle, targetDate, humanDate, ranges, hoursSum }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const vm = scope.vm;

            vm.query.GroupByCycle = cycle;
            scope._GetTableRow();
            await new Promise(resolve => setTimeout(resolve, 8000));

            const monthRow = vm.TableRowsDetail.find(r => r.EmpnoName === targetLabel || r.Name === targetName);
            if (!monthRow) throw new Error('target month row not found');
            const idx = monthRow.DaysInfo.findIndex(d => d.date === targetDate);
            if (idx < 0) throw new Error('target date not found in cycle');

            const cell = monthRow.DaysInfo[idx];
            vm.controller.HoliDayClass = true;
            vm.controller.SelDutyClass = 'ba000';
            vm.chkDutyClass = true;
            vm.chkPstn = false;
            vm.chkNotes = false;
            vm.chkCostDpt = false;
            vm.chkPlace = false;
            vm.chkWorkHoliDay = false;
            vm.controller.SelHoliDayClass = '4';
            vm.controller.SelHoliDayDutyClass = 'default';
            vm.controller.SelLeaveClass = '';
            scope._SetClass(cell, monthRow.DaysInfo, idx, monthRow.EmpnoName || monthRow.Name, monthRow);
            await new Promise(resolve => setTimeout(resolve, 2500));

            scope.GoToDayMode();
            await new Promise(resolve => setTimeout(resolve, 6000));

            const dayRow = vm.Day.Rows.find(r => (r.Name === targetName || r.Empno === monthRow.Empno) && r.Date === humanDate);
            if (!dayRow) throw new Error('target day row not found');

            const makeRange = (start, end) => ({
                Show: `${start}~${end}`,
                StartHHmm: start,
                EndHHmm: end,
                IsYesterDayToToday: false,
                Color: 'khaki',
                DutyClass: { Key: 'ba000', Color: '' },
                Job: { Key: '', Color: '' },
                Place: { Key: '', Color: '', EventName: '' },
                CostDpt: { Key: '' },
                rest_h: 0,
                lock_rest_Hours: false
            });

            dayRow.WorkRanges = ranges.map(([start, end]) => makeRange(start, end));
            dayRow.DutyClass = 'ba000';
            dayRow.Kd = '1';
            dayRow.Hdsec = '';
            dayRow.is_auto_multi = false;
            dayRow.is_work_holiday = false;
            dayRow.HoursSum = hoursSum;
            dayRow.IsChange = true;
            scope.$apply();

            const saveRow = scope.GetMultiSaveRows().find(r => (r.Name === targetName || r.Empno === monthRow.Empno) && r.Date === humanDate);
            return {
                dayRow: {
                    Name: dayRow.Name,
                    Empno: dayRow.Empno,
                    Date: dayRow.Date,
                    DutyClass: dayRow.DutyClass,
                    HoursSum: dayRow.HoursSum,
                    is_auto_multi: dayRow.is_auto_multi,
                    WorkRanges: dayRow.WorkRanges
                },
                saveRow: saveRow ? {
                    Name: saveRow.Name,
                    Empno: saveRow.Empno,
                    Date: saveRow.Date,
                    DutyClass: saveRow.DutyClass,
                    HoursSum: saveRow.HoursSum,
                    IsChange: saveRow.IsChange,
                    WorkRanges: saveRow.WorkRanges
                } : null
            };
        }""",
        {
            "targetLabel": args.target_label,
            "targetName": target_name,
            "cycle": args.cycle,
            "targetDate": args.date,
            "humanDate": format_ymd(args.date),
            "ranges": ranges,
            "hoursSum": hours_sum,
        },
    )
    return result


async def verify_multi_range_day(page, args: argparse.Namespace, target_name: str) -> dict[str, object]:
    await load_cycle(page, args.cycle)
    await page.evaluate(
        """async () => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            scope.GoToDayMode();
            await new Promise(resolve => setTimeout(resolve, 6000));
        }"""
    )
    return await page.evaluate(
        """({ targetName, humanDate }) => {
            const scope = angular.element(document.querySelector('#divWorkScheduleTable')).scope();
            const row = scope.vm.Day.Rows.find(r => r.Name === targetName && r.Date === humanDate);
            if (!row) throw new Error('verification row not found');
            return {
                Date: row.Date,
                DutyClass: row.DutyClass,
                HoursSum: row.HoursSum,
                is_auto_multi: row.is_auto_multi,
                WorkRanges: row.WorkRanges
            };
        }""",
        {"targetName": target_name, "humanDate": format_ymd(args.date)},
    )


async def run(args: argparse.Namespace) -> None:
    try:
        from playwright.async_api import async_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit("Missing dependency: playwright. Install it before running this script.") from exc

    username, password = get_credentials(args)
    target_name = args.target_name or infer_target_name(args.target_label)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.show_browser)
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
                except Exception as exc:  # pragma: no cover - debug aid
                    body = f"<body error: {exc}>"
                save_responses.append(
                    {
                        "url": response.url,
                        "status": response.status,
                        "body": body,
                    }
                )

        page.on("response", lambda response: asyncio.create_task(capture_save_response(response)))

        await login(page, args.login_url, username, password)
        await open_schedule_page(page, args.page_url)
        await add_employee_to_grid(page, args.target_label)

        if args.action == "apply-cycle-template":
            applied = await apply_cycle_template(page, args, target_name)
            await save_page(page)
            await page.reload(wait_until="domcontentloaded")
            await wait_network_idle(page)
            await page.wait_for_timeout(1500)
            await add_employee_to_grid(page, args.target_label)
            await load_cycle(page, args.cycle)
            verified_raw = await read_cycle_summary(page, args.target_label, target_name)
            verified = summarize_cycle(verified_raw["summary"], args.start_date, args.end_date, args.work_sec, args.rest_kd, args.holiday_kd)
            print("applied_counts:", applied["applied"])
            print("verified_counts:", verified)
        elif args.action == "set-multi-range-day":
            applied = await set_multi_range_day(page, args, target_name)
            await save_page(page)
            await page.reload(wait_until="domcontentloaded")
            await wait_network_idle(page)
            await page.wait_for_timeout(1500)
            await add_employee_to_grid(page, args.target_label)
            verified = await verify_multi_range_day(page, args, target_name)
            print("applied_multi_range:", applied)
            print("verified_multi_range:", verified)
        else:
            raise SystemExit(f"Unsupported action: {args.action}")

        if args.screenshot:
            screenshot_path = Path(args.screenshot).expanduser()
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print("screenshot:", screenshot_path)

        print("save_responses:", save_responses)
        await browser.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate Aurora HR work scheduling.")
    parser.add_argument("--login-url", default=LOGIN_URL)
    parser.add_argument("--page-url", default=PAGE_URL)
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--show-browser", action="store_true")
    parser.add_argument("--screenshot")

    subparsers = parser.add_subparsers(dest="action", required=True)

    cycle_parser = subparsers.add_parser("apply-cycle-template", help="Apply a recurring work/rest/holiday pattern inside a cycle.")
    cycle_parser.add_argument("target_label")
    cycle_parser.add_argument("--target-name")
    cycle_parser.add_argument("--cycle", required=True)
    cycle_parser.add_argument("--start-date", required=True, type=normalize_ymd)
    cycle_parser.add_argument("--end-date", required=True, type=normalize_ymd)
    cycle_parser.add_argument("--work-sec", required=True)
    cycle_parser.add_argument("--rest-kd", required=True)
    cycle_parser.add_argument("--holiday-kd", required=True)

    multi_parser = subparsers.add_parser("set-multi-range-day", help="Convert a day to ba000 and set explicit work ranges.")
    multi_parser.add_argument("target_label")
    multi_parser.add_argument("--target-name")
    multi_parser.add_argument("--cycle", required=True)
    multi_parser.add_argument("--date", required=True, type=normalize_ymd)
    multi_parser.add_argument("--ranges", nargs="+", required=True)

    return parser


if __name__ == "__main__":
    asyncio.run(run(build_parser().parse_args()))
