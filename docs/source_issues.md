# 抓取来源问题登记

每期运行后更新。同一来源连续两期零候选或受阻即登记，由 GPT 在隔离工作树修复，Claude 验收合并。修好后删除对应行。

| 来源 | 现象（首次登记 2026-11-25） | 原因 | 处理方向 |
|---|---|---|---|
| cset、scsp、nber、oecd-sti、ifo、nbr | 零候选 | 订阅源和列表页返回 403（网站拦截程序访问） | 改用 scripts/weekly/read_page.py 的无界面浏览器读取目录页；在此之前由 GPT 机构普查覆盖 |
| fraunhofer-isi | 14 条全部为拦截页（已正确标为 antibot） | 网站人机验证 | 同上 |
| oecd（网页） | 报告页被 Cloudflare 拦截，无界面浏览器也无法通过 | 人机验证 | 由 GPT、Gemini 检索覆盖；原文改从转载全文或 PDF 读取 |
| atlantic-council-geotech、eu-jrc、eu-stoa、alan-turing、diw、cepr、bis-research、ida-stpi、kfw-research | 零候选 | 未逐一排查 | 逐个检查列表页结构与站点地图日期字段 |
| bcg、mckinsey-mgi、pwc-research、kpmg-venture-pulse、nvca-venture-monitor | 零候选 | 低频发布且反爬 | 移出每周抓取，改为每月首周检查 |
| csis | 主题导航页（如 “On China”）被当作文章 | 列表页链接过滤不足 | 在 csis 配置中排除主题页路径 |
