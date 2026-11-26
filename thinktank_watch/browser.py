"""无界面浏览器读取：静态请求被网站拒绝（403、429 或拦截页）时，用 Chromium 打开同一网址取渲染后的网页。

浏览器按需启动、整次运行共用一个，运行结束由 close_browser() 关闭。读取失败返回 None，由调用方按原有路径处理。
"""
from __future__ import annotations

import atexit
import logging

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)
_state: dict = {}


def _page():
    if "page" not in _state:
        from playwright.sync_api import sync_playwright

        pw = sync_playwright().start()
        browser = pw.chromium.launch()
        _state.update(pw=pw, browser=browser, page=browser.new_page(user_agent=USER_AGENT, locale="en-US"))
        atexit.register(close_browser)
    return _state["page"]


def browser_html(url: str, wait_ms: int = 2500) -> tuple[str, str] | None:
    """返回 (渲染后的 HTML, 最终网址)；打不开时返回 None。"""
    try:
        page = _page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(wait_ms)
        return page.content(), page.url
    except Exception as exc:  # 浏览器任何失败都退回原路径，不中断整次抓取
        logger.warning("browser_fetch_failed url=%s error=%s", url, type(exc).__name__)
        return None


def close_browser() -> None:
    browser, pw = _state.pop("browser", None), _state.pop("pw", None)
    _state.pop("page", None)
    try:
        if browser:
            browser.close()
        if pw:
            pw.stop()
    except Exception:
        pass
