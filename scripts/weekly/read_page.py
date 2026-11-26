"""用无界面浏览器打开网页，输出正文文字（供精读时取材）。

用法：uv run python scripts/weekly/read_page.py <网址> [最多字符数，默认 20000]
"""
import sys

from playwright.sync_api import sync_playwright


def main() -> int:
    url = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"))
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        title = page.title()
        text = page.evaluate("""() => {
            const pick = [...document.querySelectorAll('article, main, [role=main]')]
                .map(e => e.innerText).filter(t => t.length > 1500)
                .sort((a, b) => b.length - a.length)[0];
            return pick || document.body.innerText;
        }""")
        browser.close()
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"TITLE: {title}\nURL: {url}\n")
    print(text[:limit])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
