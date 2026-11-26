执行本周“国际科技智库周报”。全程中文与负责人沟通；不需要中途询问，做完后简短汇报。

工作目录：C:/Users/WINDOWS/.claude/worktrees/thinktank-weekly（分支 claude/thinktank-weekly）。先 `git pull --ff-only`（失败则在当前提交上继续，并在汇报中注明）。

1. 读取 docs/weekly_sop.md，严格按其中的选材、成品结构、写法和九步流程执行。业务日期 D 为今天（北京时间，YYYY-MM-DD）。运行目录 reports/weekly_runs/D/，成品目录 briefs/weekly/<年>/D/。
2. 抓取：`uv run python -m thinktank_watch.cli audit --batch 1 --limit 30 --lookback-days 14 --date D --output reports/weekly_runs/D/audit.csv`，放后台运行。
3. 同时放后台运行两路检索（任务文字写进文件，用 -f 传）：
   - GPT 机构普查：`codex-research -f reports/weekly_runs/D/codex_sweep.md`。任务写明窗口（D-6 至 D）、要逐家检查的机构（docs/weekly_sop.md 的选材范围，以及 docs/source_issues.md 中抓取受阻的来源），要求每条给出机构、原题、日期、具体网址、类型、两三句主要发现，并列出“检查过但无新发布”的机构。
   - Gemini 议题雷达：`agy-ask <工作目录> -f reports/weekly_runs/D/gemini_radar.md`。按 SOP 的重点议题联网检索窗口内新发布，不按机构清单。
   - GPT 与 Gemini 都是基础会员，有用量上限。任务写窄、一次说清，不重复派同一件事；任何一步提示额度用尽，不等待、不反复重试：已产出的中间线索照用，这一步由你自己完成（检索自己补查，核查自己对照已下载的原文逐条核），并在 receipt.json 和汇报中写明。
4. 合并三路候选，去掉 state/articles.sqlite 和往期 briefs/weekly 已收录的条目。逐条打开原文核实日期和内容：网页用 WebFetch，被拦截时用 `uv run python scripts/weekly/read_page.py <网址>`，PDF 下载到 C:/tmp/ttsrc/D/ 后用 pypdf 提取文字。打不开原文的不收录。
5. 选题定稿前，把候选池和选题清单交给 Gemini 复核（agy-ask），逐条采纳或在 selection.md 写明不采纳理由。
6. 精读并写 briefs/weekly/<年>/D/D_国际科技智库周报.md。格式参照 briefs/weekly/2026/2026-11-25/ 样刊：导语块、本周要点、重点解读（每篇有锚点、meta 行、四格插画、摘要导读、原文链接，有可靠数据时配内联 SVG 图）、按议题分组的简讯。
6.5 插画：按 docs/weekly_sop.md 第 7.5 步，为每篇重点写四格分镜和中文说明，交 Gemini 逐张生成（GPT 备选），逐张查看后用 scripts/weekly/prepare_comics.py 转成 <成品目录>/comics/ 下的网页用图，正文用 <div class="comic"> 引用（格式见样刊）。
7. 事实核查：把一半重点和简讯交 Gemini（agy-ask，传成品目录），另一半交 GPT（codex-research，把正文附在任务文件里），要求对照原文逐条核数字、归属、状态和空话。逐条核实后修改，最多一轮。
8. 渲染：`uv run python scripts/weekly/render_issue.py <md> <成品目录>`。网页为电脑版格式（纸面居中、四格插画），用内置浏览器（先在成品目录起 `python -m http.server`）按电脑宽度看全篇，再按手机宽度看一遍；检查图表文字可读、无溢出。成品只有 HTML，不生成 PDF。
9. 归档：更新 docs/source_issues.md；把入选条目写入 state/articles.sqlite（用 thinktank_watch 的现有接口或直接插入 url 与日期）；`git add` 成品、文档和配置，提交并 `git push origin claude/thinktank-weekly`。
10. 投递：读取 config/weekly_delivery.yaml。
   - wechat_draft 为 on：`uv run python scripts/weekly/build_wechat.py <md> <成品目录>/wechat`，用内置浏览器按手机宽度查看 wechat/index.html（封面、图表、简讯分段），再用系统 Python 运行 `python C:/Users/WINDOWS/.codex/automations/automation-4/helpers/wechat_stage_issue.py <成品目录>/wechat/manifest.json`。结果须为 draft_saved_readback_verified；同一期已有草稿时它会拒绝重复新建，修改已有草稿才加 --update-existing。个人号没有接口发表权限，群发由负责人在后台操作。失败时保留本地稿件和错误原因，不影响其他步骤。
   - 不发邮件；网页版归档在成品目录即可。
11. 汇报：本期篇数、重点标题、成品路径、投递结果、仍受阻的来源。
