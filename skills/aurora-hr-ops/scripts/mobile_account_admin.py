from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path


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


async def login(page, login_url: str, username: str, password: str) -> None:
    await page.goto(login_url, wait_until="domcontentloaded")
    await page.fill("#login_name", username)
    await page.fill("#password", password)
    await page.click("#loginBtn")
    await wait_network_idle(page, timeout=20000)
    await page.wait_for_timeout(2000)


async def open_admin_page(page, page_url: str) -> None:
    await page.goto(page_url, wait_until="domcontentloaded")
    await wait_network_idle(page)
    await page.wait_for_timeout(1200)


async def search_employee(page, target_name: str):
    search = page.locator('input[type="search"][aria-controls="DataTables_Table_0"]')
    await search.fill(target_name)
    await page.wait_for_timeout(1200)
    row = page.locator("tbody tr", has=page.get_by_text(target_name)).first
    await row.wait_for(state="visible", timeout=10000)
    return search, row


async def click_if_present(locator) -> bool:
    if await locator.count():
        await locator.first.click()
        return True
    return False


async def dismiss_common_modals(page) -> None:
    if await click_if_present(page.get_by_role("button", name="確定")):
        await page.wait_for_timeout(1500)
    if await click_if_present(page.get_by_role("button", name="OK")):
        await page.wait_for_timeout(1500)


async def save_changes(page) -> None:
    save_btn = page.get_by_role("button", name="存檔")
    if await save_btn.count() == 0:
        save_btn = page.locator('input[value="存檔"]')
    await save_btn.first.click()
    await page.wait_for_timeout(2000)
    await dismiss_common_modals(page)


async def status_for_row(row) -> dict[str, object]:
    line_box = row.locator('input[type="checkbox"][ng-model="GetPeople.IsLine"]').first
    line_msg_box = row.locator('input[type="checkbox"][ng-model="GetPeople.IsLineMessage"]').first
    cancel_button_count = await row.get_by_text("取消註冊", exact=True).count()
    return {
        "row_text": await row.inner_text(),
        "line_enabled": await line_box.is_checked(),
        "line_message_enabled": await line_msg_box.is_checked(),
        "line_registered": cancel_button_count > 0,
        "cancel_button_count": cancel_button_count,
    }


async def run(args: argparse.Namespace) -> None:
    try:
        from playwright.async_api import async_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit("Missing dependency: playwright. Install it before running this script.") from exc

    username, password = get_credentials(args)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not args.show_browser)
        ctx = await browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1600, "height": 2200},
            locale="zh-TW",
        )
        page = await ctx.new_page()
        page.set_default_timeout(20000)

        await login(page, args.login_url, username, password)
        await open_admin_page(page, args.page_url)
        _, row = await search_employee(page, args.target_name)

        before = await status_for_row(row)
        print("before:", before)

        if args.action == "status":
            pass
        elif args.action == "enable-line":
            line_box = row.locator('input[type="checkbox"][ng-model="GetPeople.IsLine"]').first
            if not await line_box.is_checked():
                await line_box.check()
                await page.wait_for_timeout(800)
                await save_changes(page)
            else:
                print("LINE already enabled")
        elif args.action == "unbind-line":
            cancel_button = row.get_by_text("取消註冊", exact=True).first
            if await cancel_button.count() == 0:
                print("LINE already unbound")
            else:
                await cancel_button.click()
                await page.wait_for_timeout(1000)
                await dismiss_common_modals(page)
        else:
            raise SystemExit(f"Unsupported action: {args.action}")

        await page.reload(wait_until="domcontentloaded")
        await wait_network_idle(page)
        _, row_after = await search_employee(page, args.target_name)
        after = await status_for_row(row_after)
        print("after:", after)

        if args.screenshot:
            screenshot_path = Path(args.screenshot).expanduser()
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print("screenshot:", screenshot_path)

        await browser.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Aurora HR employee mobile account settings.")
    parser.add_argument("action", choices=["status", "enable-line", "unbind-line"])
    parser.add_argument("target_name")
    parser.add_argument("--login-url", default="https://ih5667-login.aoacloud.com.tw/Home/DeskAuthIndex")
    parser.add_argument("--page-url", default="https://erp3.aoacloud.com.tw/AU/AUAU002S00.aspx")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--screenshot")
    parser.add_argument("--show-browser", action="store_true")
    return parser


if __name__ == "__main__":
    asyncio.run(run(build_parser().parse_args()))
