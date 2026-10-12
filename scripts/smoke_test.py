"""End-to-end browser smoke test for the generated static site.

Requires: pip install playwright. Uses installed Microsoft Edge; no browser download.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = (ROOT / "dist" / "index.html").as_uri()
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> int:
    summary = json.loads((ROOT / "dist" / "data" / "summary.json").read_text(encoding="utf-8"))
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=str(EDGE), headless=True, args=["--allow-file-access-from-files"])
        desktop = browser.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True)
        page = desktop.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(SITE)
        page.wait_for_function(f"document.querySelector('#stat-new').textContent === '{summary['cards']}'")
        assert page.locator("#stat-new").inner_text() == str(summary["cards"])

        page.locator(".side-nav [data-view=cards]").click()
        assert page.locator("#card-position").inner_text().endswith(str(summary["cards"]))
        assert page.locator("#card-feedback").is_hidden()
        page.locator("#reveal-card").click()
        assert page.locator("#card-feedback").is_visible()
        page.locator("[data-rating=good]").click()
        assert page.locator("#stat-learned").inner_text() == "1"
        page.locator("#card-topic").select_option(index=1)
        assert page.locator("#card-position").inner_text().split("/")[-1].strip() != str(summary["cards"])

        page.locator(".side-nav [data-view=compare]").click()
        assert page.locator("#compare-count").inner_text() == f"{summary['comparisons']} 组"
        page.locator("#compare-search").fill("望其项背")
        assert page.locator(".comparison-card").count() >= 1

        page.locator(".side-nav [data-view=quiz]").click()
        assert page.locator("#quiz-number").inner_text() == f"题目 1 / {summary['questions']}"
        assert page.locator("#quiz-next").is_hidden()
        page.locator("[data-choice='0']").click()
        assert page.locator("#quiz-explanation").is_visible()
        assert page.locator("#quiz-next").is_visible()
        page.locator("#quiz-next").click()
        assert page.locator("#quiz-number").inner_text().startswith("题目 2 / ")
        assert page.locator("#quiz-next").is_hidden()

        page.locator("#top-settings").click()
        with page.expect_download() as download_info:
            page.locator("#export-progress").click()
        download = download_info.value
        assert download.suggested_filename.startswith("zhixu-progress-")
        page.locator("#settings-dialog .dialog-head button").click()

        phone = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        mobile_page = phone.new_page()
        mobile_page.goto(SITE)
        mobile_page.wait_for_function(f"document.querySelector('#stat-new').textContent === '{summary['cards']}'")
        sizes = mobile_page.evaluate("({width: innerWidth, scrollWidth: document.documentElement.scrollWidth})")
        assert sizes["scrollWidth"] <= sizes["width"], f"手机页面横向溢出：{sizes}"
        assert mobile_page.locator(".mobile-nav button").count() == 5
        mobile_page.locator(".mobile-nav [data-view=cards]").click()
        assert mobile_page.locator("#flashcard").is_visible()
        assert mobile_page.locator("#card-feedback").is_hidden()
        browser.close()
    assert not errors, f"浏览器脚本错误：{errors}"
    print(f"浏览器冒烟测试通过：{summary['cards']} 张词卡、{summary['comparisons']} 组辨析、{summary['questions']} 道题；桌面和 390px 手机布局可用。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"浏览器测试失败：{exc}", file=sys.stderr)
        raise

