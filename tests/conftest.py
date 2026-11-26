import pytest

import thinktank_watch.fetch as fetch_module


@pytest.fixture(autouse=True)
def no_real_browser(monkeypatch):
    """测试不启动真实浏览器；需要浏览器结果的测试自行替换 browser_html。"""
    monkeypatch.setattr(fetch_module, "browser_html", lambda url: None)
