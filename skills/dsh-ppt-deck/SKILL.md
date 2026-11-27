---
name: dsh-ppt-deck
description: 帮我做一份后面还能改的 PPT，或把这份 PowerPoint 的版式、字体和图表改一改。
whenToUse: 用户说「做份能编辑的汇报 PPT」「改一下这份 .pptx」「图表和文字我还要自己改」。不适用：「用 Beamer 做一份，PPT 能放映就行」或「只帮我润色讲稿」。
---

# 制作和修改可编辑 PPT

先定分页大纲，用 Python 生成可编辑的 PowerPoint，交付前渲染逐页检查。

## 任务路由

| 用户要做什么 | 读哪里 |
|---|---|
| 新做可编辑 PPT、改现有 PPT 的版式或字体 | [制作和修改幻灯片](references/create-or-revise-deck.md) |
| 修阴影、中文字体、标题压线 | [修版式问题](references/fix-slide-layout.md) |
| 渲染或检查已有 PPTX | [渲染和验收](references/render-and-qa.md) |
| 只说「做个答辩 PPT」，交付格式未定 | 问「交付后要在 PowerPoint 里继续改文字和图表吗？」 |
| 指定 Beamer，接受逐页图片的 PPTX | 见 [academic-slide-deck](../academic-slide-deck/SKILL.md) |

## 最小流程

1. 给 6–10 屏的分页大纲，每页写一句结论和要放的素材，确认后再写代码。
2. 用 [代码骨架](assets/deck_kit.py) 生成幻灯片，每 3–5 页渲染一次。改现成 PPTX 时先确认要保留的页、对象和备注。
3. 保存带版本号的 PPTX，运行结构检查与全页渲染，按门禁记录问题页码后再交付。

## 门禁

- **页序与主体**：将大纲和 PPTX 逐页对照，页数及页序一致，每页只有 1 个视觉主体。
- **逐页视觉验收**：逐张打开最终版的 PNG，检查元素重叠、换行压线、图文越界、留白失衡及图内文字可读性，记录每处问题的页码和位置。
- **可编辑性**：在 PPTX 里选中需要编辑的文字、图表和流程图。图表与流程图使用原生对象，数据可回到脚本。
- **结构与字号**：运行 `d.verify()`，问题列表为空。正文在 PPTX 中逐页核对 ≥18pt，小字号检查提示逐条区分正文和图注等例外。
- **备注**：逐页打开备注，对照大纲检查每页非空，讲稿覆盖本页结论和需要解释的图表。
- **版本**：核对输出文件名带版本号，交付前后旧版本文件仍在。

## 相关技能

- [academic-slide-deck](../academic-slide-deck/SKILL.md) 负责 Beamer、PDF 和逐页图片 PPTX。
- [humanize-writing](../humanize-writing/SKILL.md) 用于润色现有讲稿。
- [longform-report](../longform-report/SKILL.md) 用于先完成多来源长报告再做幻灯片。
