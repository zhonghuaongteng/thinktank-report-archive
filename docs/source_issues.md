# 抓取来源问题登记

每期运行后更新。同一来源连续两期零候选或受阻即登记并排查：能修的改入口；网站失效、浏览器也无法通过验证或内容与研究关注无关的，把 batch 改为 3 移出每周抓取并在 notes 写明原因；同时补充同类议题的权威来源。修好后删除对应行。

最近一次全量核对：2026-11-27（54 个每周来源，零候选 11 个，窗口内候选 141 条；核对前为 53 个来源、零候选 20 个、窗口内 97 条）。

## 仍需处理

| 来源 | 现象 | 判断 | 下一步 |
|---|---|---|---|
| bis-research | 新配的工作论文订阅源未产出候选 | 订阅源本身可读（25 条），推测被领域或路径过滤挡掉 | 检查允许域名与路径过滤 |
| bis-innovation-hub、epoch-ai、nesta、ukri、kistep（2026-11-27 新增） | 零候选 | 列表页浏览器可读，链接提取未命中文章路径 | 逐个调整列表页或允许路径段 |
| cepr、eu-jrc、eu-stoa、kfw-research、nvca-venture-monitor | 零候选 | cepr 间歇性人机验证；其余页面可读但未提取到文章 | 逐个检查页面结构，必要时改用订阅源 |
| oecd-sti | 16 条候选、15 条原文页被人机验证拦截 | 论文系列页可读，单篇页仍被拦 | 由 GPT、Gemini 检索补原文；评估改用出版物 PDF 直链 |
| nbr | 8 条候选、7 条原文页失败 | 原文页人机验证 | 同上 |
| ncses | 6 条候选、5 条原文页失败 | 待查 | 检查原文页地址格式 |
| csis | 主题导航页（如 “On China”）被当作文章 | 列表页链接过滤不足 | 在 csis 配置中排除主题页路径 |

## 2026-11-27 已处理

- 抓取程序新增浏览器读取：静态请求被拒（403、429 或拦截页）时，列表页和原文页自动改用无界面浏览器再取，救回 cset、nber、korea-msit、atlantic-council-geotech、diw 等。
- 修入口：bis-research 改读工作论文订阅源；scsp 加订阅源；jst-crds 改读日文报告目录；oecd-sti 改读论文系列页。
- 移出每周抓取（batch 3）：ida-stpi（网站改版入口失效）、ifo（浏览器也无法通过验证）、mckinsey-mgi（长期超时）、bcg、pwc-research、kpmg-venture-pulse、deloitte-insights、bain-research（企业经营内容为主）、eib-research（只抓到筛选页）。
- 新增：royal-society、nesta、rieti、bis-innovation-hub、ukri、rori、kistep、ncses、nasem、epoch-ai。其中 rieti、royal-society、rori 已正常产出。
