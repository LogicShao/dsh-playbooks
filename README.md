# dsh-skills

给 DeepSeek Harness（DSH）用的技能仓库。每个技能是一个自包含目录，带自己的版本号和更新记录，可以装进任意项目的 `.dsh/skills/`，也可以装到 profile 里全局生效。

所有技能都按同一条原则写：**先讲清什么时候用、再给流程和阈值、最后给可验收的出口**。没有素材时不编，规则宁少勿多。

## 技能

| 技能 | 版本 | 什么时候用 | 一句话 |
|---|---|---|---|
| [dsh-ppt-deck](skills/dsh-ppt-deck/SKILL.md) | 1.0.0 | 做 PPT、汇报材料、答辩稿、课件；或改一份现成的 .pptx | 先大纲后脚本，python-pptx 生成，渲染成 PNG 逐页看图 |
| [academic-slide-deck](skills/academic-slide-deck/SKILL.md) | 1.0.0 | 组会、翻转课堂、开题、答辩，想要 Beamer 质感 | LaTeX Beamer → PDF → 逐页图 PPTX + 讲稿 |
| [humanize-writing](skills/humanize-writing/SKILL.md) | 1.0.0 | 去 AI 味、写得更像人、模仿某人文风 | 删 → 换 → 补 → 读，四步减法 |
| [longform-report](skills/longform-report/SKILL.md) | 1.0.0 | 综述、调研报告、白皮书、实验报告，超过三五页 | 七步流水线：调研 → 台账 → 写作 → 独立复核 → 版式验收 |
| [research-align](skills/research-align/SKILL.md) | 1.0.0 | 科研写作、改稿、审稿回复，怕它写偏或编文献 | `.research/` 三件套 + 复述握手 + 四道闸门 |

两个 PPT 技能的分工：要**可编辑的 pptx**、以代码驱动排版，用 `dsh-ppt-deck`；要**Beamer 的排版质量**、接受 PPTX 是逐页图，用 `academic-slide-deck`。

## 安装

技能是纯目录，不需要构建。DSH 从这两处发现技能，目录名必须等于 `SKILL.md` 里 frontmatter 的 `name`：

- 项目级：`<项目>/.dsh/skills/<技能名>/SKILL.md`
- 用户级：`~/.dsh/skills/<技能名>/SKILL.md`（`%USERPROFILE%\.dsh\skills`）

项目级优先于用户级；两处同名时以项目里那份为准。

```powershell
# 装到某个项目
pwsh ./scripts/install.ps1 -Target D:\proj\my-project

# 只装一个
pwsh ./scripts/install.ps1 -Target D:\proj\my-project -Skill humanize-writing

# 装到 profile，所有项目都能用
pwsh ./scripts/install.ps1 -Target profile

# 先看会动哪些文件
pwsh ./scripts/install.ps1 -Target D:\proj\my-project -DryRun
```

默认**不覆盖**已经有本地改动的副本；确认要覆盖时加 `-Force`，想留旧版加 `-Backup`。

## 版本与同步

每个技能独立做语义化版本，仓库根的 [manifest.json](manifest.json) 记录每个文件的 sha256，用来判断「装的那份是不是被改过」。

| 改动类型 | 版本位 | 例子 |
|---|---|---|
| 触发条件、流程骨架变了，旧用法会失效 | major | 把「五步握手」改成三问三答 |
| 新增章节、模板、任务配方 | minor | 加一类任务配方 |
| 改错字、修路径、补示例、调措辞 | patch | 换成自动发现 LibreOffice Kit 路径 |

标签格式 `<技能名>/v<版本>`，例如 `dsh-ppt-deck/v1.0.0`：

```powershell
git tag -l "dsh-ppt-deck/*"          # 看某个技能的历史版本
git checkout dsh-ppt-deck/v1.0.0     # 回到某个稳定版本再安装
```

日常三条命令：

| 目的 | 命令 |
|---|---|
| 看已装副本和仓库差在哪 | `pwsh ./scripts/status.ps1 -Target D:\proj\my-project` |
| 同步到最新 | `pwsh ./scripts/install.ps1 -Target D:\proj\my-project -Force` |
| 提交前自检 | `pwsh ./scripts/validate.ps1` |

**为什么用复制而不是目录链接**：junction 永远指向工作区，等于永远跟着 HEAD 走，没法钉版本；复制出来的副本配合 `VERSION` 和清单哈希，才能回答「这个项目当时用的是哪一版、后来有没有被手改」。要改技能就改仓库里的，再用 `install.ps1` 覆盖回去。

## 目录结构

```
dsh-skills/
├─ manifest.json              # 版本 + 每个文件的 sha256，由 scripts/manifest.ps1 生成
├─ skills/
│  ├─ dsh-ppt-deck/
│  │  ├─ SKILL.md             # 给模型看的正文
│  │  ├─ VERSION              # 语义化版本
│  │  ├─ CHANGELOG.md         # 该技能的更新记录
│  │  └─ assets/deck_kit.py   # 可直接复制的代码骨架
│  └─ ...
├─ scripts/
│  ├─ lib.ps1                 # 哈希、清单、路径解析
│  ├─ manifest.ps1            # 重建 manifest.json
│  ├─ validate.ps1            # frontmatter / 内链 / 绝对路径 / 清单一致性
│  ├─ install.ps1             # 安装或同步到项目 / profile
│  ├─ status.ps1              # 只读对比
│  └─ bump.ps1                # 升版本 + 写 CHANGELOG + 重建清单
└─ .github/workflows/validate.yml
```

## 改完怎么发版

```powershell
pwsh ./scripts/bump.ps1 -Skill dsh-ppt-deck -Part patch -Note "补渲染失败时的报错信息"
pwsh ./scripts/validate.ps1
git add -A
git commit -m "dsh-ppt-deck v1.0.1：补渲染失败时的报错信息"
git tag dsh-ppt-deck/v1.0.1
git push --tags
```

`validate.ps1` 会拦住这几种情况：frontmatter 缺字段、`name` 与目录名不一致、引用了不存在的 `assets/` 或 `references/` 文件、正文里写死本机绝对路径、改了内容但忘了重建 manifest。

## 许可

MIT，见 [LICENSE](LICENSE)。
