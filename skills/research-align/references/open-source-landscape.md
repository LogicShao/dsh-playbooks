# 外部工具与开源项目

## 一、选工具时检查什么

| 要完成的任务 | 选工具时检查什么 |
|---|---|
| 补查文献 | 可导出检索式、命中数和去重记录，按[文献综述配方](task-recipes.md#1-文献综述)复跑 |
| 导出书目 | 至少试导一条 DOI，逐项比对出版页面的作者、标题和年份 |
| 精读全文 | 输出的主张、方法和局限能回填[证据台账](../assets/claim-evidence.md)，能定位到原句 |
| 遴选外部程序 | 使用前查看许可与最近提交，先用一条公开材料试跑，再决定是否批量使用 |
| 做成交付件 | 成稿润色见 `humanize-writing` 技能，可编辑幻灯片见 `dsh-ppt-deck` 技能 |

默认依赖已有项目材料。需要联网核验时，按[引文核验清单](verification.md)记录来源。跨会话的简报、证据和决策仍写回项目文件，便于复查。

## 二、可借鉴的开源项目

> 调研时间：2026-11。以下项目均可公开访问；社区变化快，使用前先看 LICENSE 和最近提交。

| 项目 | 定位 | 值得借的做法 |
|---|---|---|
| [metravod/omut](https://github.com/metravod/omut) | 给 agent 用的项目记忆（普通 markdown + 校验 CLI） | `brief.md`（why/what/where/now/next）+ `decisions.md`（带状态）+ `threads/` + 日志；事实声明要写「怎么核 + 最后核对日期」；体积预算（brief 60 行）；`dream` 定期整理记忆 |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 学术全流程技能套件（研究→写作→评审→返修） | **Material Passport** 跨阶段状态文件；**主张级引文锚点** + claim audit；**Knowledge Isolation**（材料优先，缺内容标 `[MATERIAL GAP]` 而不是脑补）；integrity gates；anti-context-rot 锚点；反谄媚/Devil's Advocate；Style Calibration |
| [Norman-bury/research-writing-skill](https://github.com/Norman-bury/research-writing-skill) | 中文科研写作技能系统（v3.1） | 开工前 **7 轮头脑风暴对齐**（论文类型/学科/方法/结构）；`plan/progress.md`；引言前先有 `evidence-map`；实验前先有 protocol/schema/manifest；**Red Flags 表**（AI 的合理化念头 → 正确行为）；两阶段 Review |
| [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills) | 基于彭思达公开笔记的 ML/CV/NLP 论文写作技能 | 论文写作方法论的技能化（故事线、贡献表达、审稿视角） |
| [O0000-code/awesome-academic-skills](https://github.com/O0000-code/awesome-academic-skills) | 222 个学术 agent 技能的索引（按科研生命周期分类，CC0） | 选型地图：检索/精读/写作/审稿各阶段现成技能一览 |
| [yanzhanlin/literature-review-skill](https://github.com/yanzhanlin/literature-review-skill) | 端到端文献综述（PRISMA-S、PICO/SPIDER） | 可复现检索日志、系统综述方法论 |
| [O0000-code/paper-search-pro](https://github.com/O0000-code/paper-search-pro) | OpenAlex 主导的五源检索 | 检索饱和曲线 + 停止决策 + HTML 报告 |
| [MilkClouds/fetch-bib](https://github.com/MilkClouds/fetch-bib) | 人工确认的 BibTeX 获取 | 每个字段从出版方/DBLP 拉取，带 provenance，歧义就停下来问 |
| [njzjz/wenxian](https://github.com/njzjz/wenxian) | DOI/PMID/arXiv → BibTeX | 元数据核验的现成 CLI |
| [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | 深度研究技能 | 每条断言对来源做 CrossRef 核验、引用跨压缩持久化 |
| [dailypaper-skills](https://github.com/huangkiki/dailypaper-skills) / [deeppapernote](https://github.com/917dhj/deeppapernote) | 论文精读与结构化笔记 | 主张/方法/要点的笔记结构，便于回流到证据台账 |
| [daaf](https://github.com/daaf-contribution-community/daaf) | 可复现量化研究框架 | 可审计步骤、守卫、人类复核 |

## 三、这些项目的共同模式

1. **状态文件跨会话持久化**：Material Passport / brief / memory——不靠聊天记录对齐。
2. **材料优先、缺材料就标缺口**：Knowledge Isolation 的 `[MATERIAL GAP]` 比「编一个合理内容」安全一个量级。
3. **主张级引文锚点 + 门禁**：不是「有参考文献」，而是「这句话对应原文哪一句」。
4. **流程门禁 + Red Flags**：把「AI 会怎么偷懒」写成清单，触发即停。
5. **人类签核**：关键判断（新颖性、因果、伦理）保留人工确认点，不做全自动。

## 四、本技能的取舍

| 取舍 | 原因 |
|---|---|
| 轻量，只做「对齐」这一层 | 上面几个套件是重型多 agent 系统，安装/配置成本高；日常科研最痛的其实是对齐 |
| 状态只有三个文件（brief / claim-evidence / decisions） | 5 分钟能建好，维护成本低；文件多了没人更新 |
| 默认不联网 | 核验工具按需调用；模型不联网时也能工作 |
| 中文优先 | 术语表、任务配方按中文学术写作习惯组织 |
| 不重复检索/排版能力 | 检索交给 paper-search-pro 等；docx/PPT 交给 office 技能；成文去 AI 味交给 `humanize-writing` |

## 五、组合建议

```
对齐（本技能） → 检索（paper-search-pro / literature-review-skill）
             → BibTeX（fetch-bib / wenxian）
             → 精读（dailypaper-skills）
             → 成文（humanize-writing）
             → 交付（office-docx / office-pptx）
```

## 六、参考来源

- omut README 与规范：https://github.com/metravod/omut
- ARS 架构与 Material Passport：https://github.com/Imbad0202/academic-research-skills
- research-writing-skill 质量门控与 Red Flags：https://github.com/Norman-bury/research-writing-skill
- 学术技能索引：https://github.com/O0000-code/awesome-academic-skills
