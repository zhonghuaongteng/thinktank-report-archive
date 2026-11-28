# 抓取来源问题登记

每期运行后更新。完整抓取后先把零候选的来源单独重跑一次，排除中途断网。同一来源连续两期零候选或受阻就登记并排查：能修的改入口；网站失效、浏览器也无法通过验证或内容与研究关注无关的，把 batch 改为 3 移出每周抓取，并在 notes 写明原因；同时补充同类议题的权威来源。不经代理或其他方式绕过网站对本机的封锁。修好后删除对应行。

最近一次全量核对：2026-11-29。51 个每周来源，零候选 0 个，候选 594 条，近 7 天 163 条，原文页读取成功 557 条、失败 31 条。2026-11-27 核对前为 53 个来源、零候选 20 个、近 7 天 97 条。

## 仍需处理

| 来源 | 现象 | 判断 | 下一步 |
|---|---|---|---|
| oecd-sti | 16 条候选，原文页全部被人机验证拦截 | 论文系列页可读，单篇页连浏览器也被拦 | 由 GPT、Gemini 检索补原文；评估改用出版物 PDF 直链 |
| nbr | 8 条候选，原文页全部失败 | 原文页人机验证 | 同上 |
| alan-turing | 3 条候选，原文页均被拦截，且混入栏目页 | 网站对原文页启用验证 | 观察一期；仍受阻则移出每周抓取，另找英国 AI 研究来源 |

## 2026-11-29 已处理

- 零候选的 11 个来源已全部修好或移出：bis-research、ukri、epoch-ai、nesta、bis-innovation-hub、eu-jrc、eu-stoa、kistep 改了入口或文章路径规则；cepr、kfw-research、nvca-venture-monitor 移出每周抓取。
- 英国皇家学会对本机的直接访问和浏览器访问都返回拦截页，已移出每周抓取，改由英国皇家工程院（raeng）替补。
- 浏览器读取改为等网页加载完成后再取，修好靠脚本延迟加载列表的网站。
- 原文页跳转只核对网站域名，修好 ncses。CSIS 排除专题导航页，并合并同一篇的两种地址写法。

## 2026-11-27 已处理

- 抓取程序新增浏览器读取：静态请求被拒（403、429 或拦截页）时，列表页和原文页自动改用无界面浏览器再取，救回 cset、nber、korea-msit、atlantic-council-geotech、diw 等。
- 修入口：bis-research 改读工作论文订阅源；scsp 加订阅源；jst-crds 改读日文报告目录；oecd-sti 改读论文系列页。
- 移出每周抓取（batch 3）：ida-stpi（网站改版入口失效）、ifo（浏览器也无法通过验证）、mckinsey-mgi（长期超时）、bcg、pwc-research、kpmg-venture-pulse、deloitte-insights、bain-research（企业经营内容为主）、eib-research（只抓到筛选页）。
- 新增：royal-society、nesta、rieti、bis-innovation-hub、ukri、rori、kistep、ncses、nasem、epoch-ai。
