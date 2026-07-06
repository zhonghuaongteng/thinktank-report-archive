# 周报 Codex 漫画生成流程

## 固定模式

周报默认采用“目录 -> 本周态势 -> P0/P1 逐主题页”的阅读结构。每条 P0/P1 主题页嵌入一张 Codex 生成漫画，漫画用于解释报告核心观点、关键机制和政策含义。

本模式已经取代早期的程序化示意图、1-3页集中导读漫画和“主题机制图解”。后续周报不得回退为程序化示意图，也不得回退到 SVG、Pillow、ReportLab 绘制的流程图或占位图。

## 漫画叙事规则

- 每张漫画锚定一篇报告或一条 P0/P1 主题。
- 画面应回答：报告识别了什么信号、核心机制或矛盾是什么、报告的政策含义是什么、最重要的结论是什么。
- 最后一格或最后一页不强行落到中国或上海；只有报告本身、摘要或主题标签存在明确涉华、涉沪或可操作参照时，才纳入中国/上海内容。
- 没有明确中国/上海参照时，漫画应以报告核心观点收束。
- 图片中文字只保留短标题、路标和标签；精确研判写在周报正文卡片中。

## 自动化顺序

1. 运行 `scripts\run_weekly.ps1 -Batch 1 -Limit 30` 完成周频抓取、归档、状态库、知识库索引和初版周报。
2. 运行 `scripts\prepare_weekly_comics.ps1 -Date <YYYY-MM-DD>`，为当期 P0/P1 主题生成提示词：
   - `comic/weekly-topic-comics-<YYYY-MM-DD>/prompts/*.md`
   - `comic/weekly-topic-comics-<YYYY-MM-DD>/manifest.md`
3. 对每个提示词调用 Codex 内置图片生成能力，输出到同目录 `pages/`，文件名与提示词同名，扩展名使用 `.jpg`。
4. 运行 `scripts\render_weekly_brief.ps1 -Date <YYYY-MM-DD>`，从本地归档重建周报，使 Markdown、HTML 和 PDF 引用真实漫画。
5. 运行 `scripts\check_weekly_comics.ps1 -Date <YYYY-MM-DD>`，确认提示词、图片、Markdown、HTML 和 PDF 数量一致，并确认没有占位语或旧示意图术语。

## 质量闸门

- `prompt_count`、`comic_count`、`md_image_refs`、`html_image_nodes`、`pdf_image_count` 均不得小于当期 P0/P1 条目数。
- `blocked_hits` 必须为空。
- PDF 抽样页应显示真实漫画，不能是空白、占位图或程序化示意图。
- 如某张漫画生成失败，可以保留该期周报生成失败状态并报告，不得用程序化图替代。
