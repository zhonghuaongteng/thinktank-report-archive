# 周报启动恢复

2026-11-16修订用于automation-4。权威本机运行规则仍为 `C:/Users/WINDOWS/.codex/docs/agent-rules/automations/automation-4.md`；本文件与代码提供可追溯的项目副本。

旧入口可能来自已停止更新的main。设置upstream只改变跟踪关系，不改变起点；从旧HEAD建分支再pull会出现无法快进。2026-11-08记录的1/245分叉即由此产生。本地独有1个提交是7月6日历史日报归档，不能通过重置删除。

## 启动

先固定北京时间业务日期D，再用已验证Python调用 `scripts/prepare_weekly_worktree.py --entry <调度器入口> --date <D>`。生产提示使用自动化目录下同源码的固定路径，以便旧入口也能找到修复后的程序。默认目标是已授权的origin/codex/backfill-govai-interface-oecd，默认登记目录是用户.codex/automations/automation-4/runs。

- `new_from_verified_remote`：联网核验远端提交与最低版本祖先，从该提交建立新干净隔离工作树。旧入口分叉或脏时保持原样。
- `resume_existing`：在已登记或实际开始工作的同一期工作树接续。先检查活动任务、采集进程和现有检查点，不重复采集，不再用pull改变已开始工作的基线。
- `verify_already_sent`：核对Gmail SENT和附件，跳过采集与发信；仅在有待同步记录时继续备份。

错误远端、不可证实的最低版本、无法取得可信基线以及含糊的多个活动工作树不能假冒成功。先修复可恢复原因，仍无法解决时报告具体阶段。准备阶段有OS文件锁；它不替代后续执行任务的协调和发送查重。

## 同步与投递

内容与附件质量、Git备份、OneDrive同步、邮件分阶段记录。Git同步故障不单独否决已验收邮件；保留本地提交、实际附件路径与哈希和待同步记录，如实说明。OneDrive脏副本不stash、reset、clean或覆盖；不强制推送。邮件按automation-4、D、准确收件人与主题查重，尝试次数跨接续累计。状态不明先查SENT，不以重发解决。

## 验证

回归测试 `tests/test_weekly_worktree_bootstrap.py` 用临时仓库实际复现1/245分叉，验证dirty文件保留、同日期复用、已发送不重启、错误远端/版本/抓取、内容数组与纯预检树等场景；不调用生产采集或邮件。维护回执见 `docs/run_receipts/2026-11-16_automation_maintenance.json`。源码修改后，同步生产固定路径与仓库副本并核对哈希。
