---
name: academic-slide-deck
description: 用 Beamer 排一份组会或答辩 PPT，给我 PDF、能放映的 PPTX 和逐页讲稿，或把现成的 Beamer PDF 转成 PPT。
whenToUse: 用户说「用 Beamer 做答辩」「给我 PDF 和能放的 PPT，整页是图也行」「把这份 Beamer PDF 转 PPT」。不适用：「PPT 里的文字和图表还要能改」或「只帮我润色讲稿」。
---

# 制作 Beamer 汇报和逐页图 PPTX

维护 Beamer 源稿，从同一版本导出 PDF、逐页图片 PPTX 和约定的讲稿。

## 任务路由

| 用户要做什么 | 读哪里 |
|---|---|
| 新做或改组会、课堂、开题、答辩的 Beamer 源稿 | [制作 Beamer 汇报](references/create-beamer-deck.md) |
| 从源稿导出 PDF、PPTX 或将已有 Beamer PDF 转 PPTX | [导出和验收幻灯片](references/export-and-qa.md) |
| 写逐页讲稿或导出讲稿 PDF | [写讲稿和导出](references/prepare-speaker-script.md) |
| 只说「做个答辩 PPT」，交付格式未定 | 问「交付后要在 PowerPoint 里继续改文字和图表吗？」 |

## 最小流程

1. 定受众、场合、目标时长、输出格式和研究拓展点，登记源稿和交付物。
2. 确认分页内容脚本，再制作实验图并核对数字来源。
3. 实现 Beamer 源稿并编译 PDF，按页准备备注和讲稿。
4. 按约定导出 PPTX 与讲稿 PDF，运行适用门禁，再把最终文件放进专用目录。

## 门禁

- **编译**：按导出配方运行 XeLaTeX 两遍，日志中的 error、Overfull、Underfull 均为 0。
- **页数与备注**：从源稿导出时，运行配方里的校验命令，要求 PDF 页数、PPTX 页数、非空备注数、frame 数相等。仅转换 PDF 且约定无备注时，只比对 PDF 与 PPTX 页数。
- **逐页画面**：按导出配方渲染 PNG。一页一个视觉主体及 PNG 视觉检查见 [dsh-ppt-deck 的门禁](../dsh-ppt-deck/SKILL.md#门禁)。逐页测底部留白 ≥10mm，记录未过页码。
- **页面文字与数字**：去掉 note 后，页面文字的 `；`、`——` 和教材、定理编号均为 0。逐项对照数字回填清单，拓展页结果数字为 0。
- **讲稿**：逐页计时，合计在目标时长 ±10 秒内。在内容脚本与讲稿里检索旧标题和旧时长，命中为 0。
- **交付目录**：列出目录内容，对照交付树检查最终文件，清除 aux、log、nav 及临时预览和测试文件。

## 相关技能

- [dsh-ppt-deck](../dsh-ppt-deck/SKILL.md) 用于直接做可编辑 PPTX。
- [humanize-writing](../humanize-writing/SKILL.md) 用于润色现有讲稿。
- [research-align](../research-align/SKILL.md) 用于核对组会报告的研究材料和引文。
