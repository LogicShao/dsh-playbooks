---
name: academic-slide-deck
description: Build or rework academic presentation decks (组会汇报 / 翻转课堂 / 开题 / 答辩 / 课程汇报) as Beamer-quality 16:9 slides, exported to PDF + image-based PPTX with speaker notes, plus a matching speaker script.
whenToUse: The user asks to create, revise, export, or review a research/teaching slide deck (组会、翻转课堂、开题、答辩、课程汇报); asks for a Beamer/LaTeX deck with PPTX output; asks for speaker notes/讲稿 for slides; or asks to convert a Beamer PDF to PPTX.
---

# 学术汇报 PPT 工作流（组会 / 翻转课堂 / 开题 / 答辩）

一句话：**LaTeX Beamer → PDF → PPTX（逐页图 + 备注），外加一份讲稿。只改源文件，不手改导出物。**

## 目录与交付契约

**源文件/工作区**（改这些，留在原位）：

- `03_slides/PPT内容脚本.md`：每页 `标题｜时长｜视觉主体｜页面文字｜备注`，页序的唯一事实源；
- `03_slides/beamer/main.tex`：deck 源文件（可加一个极简 `svmstyle.sty`）；
- `03_slides/讲稿.md`：每页【要点】/【口播】/【追问备用】；
- `02_experiments/` + `数字回填清单.md`：可复现实验、图、页面/讲稿数字的唯一来源；
- 根目录 `README.md`：五六行“想讲/想改/想复现”分别打开什么。

**交付物**（只放最终文件，单独一个目录）：

```
05_交付/                    # 默认目录名；也可用 deliverables/，但必须独立成目录
├── deck.pdf                # 正片，以此为准
├── deck.pptx               # 逐页图 + 备注，可直接放映
├── 讲稿.pdf                # 可打印
├── 课堂任务单与评价量规.md   # 如有
└── README.md               # 一页说明：里面是什么、源文件在哪、怎么重建
```

硬性约定：**最终交付物统一放这个专用目录**，不要平铺在项目根、`03_slides/` 或源文件旁边；交付目录里只放能直接发/上传/打印的文件，不放 `.aux/.log`、中间图、测试 PDF。交付=直接压缩这个目录。

## 硬性风格（默认，可被用户覆盖）

1. `ctexbeamer`、`aspectratio=169`、`10pt`、`fontset=windows`、default 主题、xelatex。
2. 无页码、无目录、无章节标签、无导航、无装饰色块。
3. 名词短语标题；一页一个视觉主体（图/公式/表/TikZ）；页面文字删到只剩一句结论。
4. 页面不写教材/定理编号（`教材式(6.34)`、`定理 6.2`），细节与数字进 `\note{}` 和讲稿。
5. 页面文字不出现 `；`、`——`，不用“我们来看/大家注意/值得强调”。
6. 研究/拓展页不放结果数字（准确率、Dice、p 值）；数字只进备注/追问。
7. 除结束页外不写“谢谢”；结束页只写「谢谢」并回扣开场意象。
8. 每页都有 `\note{}`；导出时按 frame 顺序写入 PPTX 备注。
9. PPTX 是 1920×1080 逐页图，视觉与 PDF 一致但不可编辑；改内容改 tex 重编译再导出。
10. 用户说“删到不可再删”时，删页面文字，知识点下沉到讲稿/备注。
11. **交付物集中存放**：最终 PDF/PPTX/讲稿 PDF 只放一个专用交付目录（默认 `05_交付/`），源文件留在工作目录；交付目录里不放中间产物，也不要把生成物和源文件混在一起。

## 流程

0. **定契约**：受众、场合、时长（15–20 分钟；把目标时长写进 README，例如 19 分 20 秒记作 19:20，这是“时长”不是“时刻”）、是否要可编辑 PPTX、用户研究拓展点，写进 README。
1. **先写内容脚本**：每页 `标题｜时长｜视觉主体｜页面文字（≤1 行）｜备注`；页序先确认再动 LaTeX。
2. **先做证据**：实验固定 seed；图 2400×1350、200 dpi、微软雅黑；幻灯片专用图另存，不覆盖实验原图；数字进回填清单。
3. **Beamer 实现**：一帧一页；TikZ 画示意图，matplotlib 画数据图；每帧 `\note{}`。
4. **编译**：`xelatex -interaction=nonstopmode main.tex` 跑两遍；0 error、Overfull/Underfull = 0。
5. **讲稿**：每页三段；【口播】按 240 汉字/分钟，总量≈时长；公式用 `$...$`；数字与清单一致。
6. **验收**（下节）通过后再交付。

## 导出 PDF + PPTX

PDF 复制到 `05_交付/deck.pdf`；PPTX 输出到 `05_交付/deck.pptx`；讲稿 PDF 也放这里。PPTX 转换要用同时装了 `pymupdf` 和 `python-pptx` 的解释器，先确认再动手：

```powershell
& "$py" -c "import pymupdf, pptx; print('ok')"
```

DSH 自带的 Python 只有 `python-pptx`，缺 `pymupdf`，直接用它会在 `import pymupdf` 处报错。

```python
import os
import pymupdf
from PIL import Image
from pptx import Presentation
from pptx.util import Emu

notes = parse_notes_from_tex("main.tex")          # 按 frame 顺序取 \note{...}（正则从略：先删整行注释，再对每个 frame 搜 \\note\{(.*?)\}）
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)   # 13.333×7.5 in
for idx, page in enumerate(pymupdf.open("main.pdf")):
    zoom = 1920 / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    tmp = f"._p{idx:02d}.png"
    img.save(tmp)
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_picture(tmp, 0, 0, width=prs.slide_width, height=prs.slide_height)
    os.remove(tmp)
    if notes:
        s.notes_slide.notes_text_frame.text = notes.pop(0)
prs.save("deck.pptx")
```

要点：整页铺满、无白边；备注 1:1；PPTX 在 PowerPoint 中打开时写入会失败，关闭或重试。

## 验收门禁（必须报数字）

- **计数**：PDF 页数 = PPTX 页数 = 非空备注数 = frame 数；每帧都有 note；
- **视觉**：逐页渲染成 PNG 检查，不压线、不重叠、不出界、图内文字可读；
- **留白**：每页底部 ≥ 10mm（11mm 更稳）；不足时先整体上移/压间距，再缩图 2–4mm；
- **文字**：页面文字（去掉 note 后）`；`、`——` 为 0，无教材/定理编号；
- **数字**：与 `数字回填清单.md` 一致；拓展页无结果数字；
- **讲稿**：总时长 = 目标 ±10 秒；旧页名/旧时间 grep 为 0；
- **交付目录**：`05_交付/` 里只有最终 PDF/PPTX/讲稿/任务单/README，无 aux/log/中间图/测试文件；
- **清理**：删 `_check_*.png`、`.aux/.log/.nav` 等临时文件。

底部留白速测：2x 渲染每页，找最低非白行，`margin_mm = (h-1-last_row)/2*0.3528`；低于阈值就报页码。

## 讲稿可选导出 PDF

```powershell
pandoc "讲稿.md" -o "05_交付/讲稿.pdf" --pdf-engine=xelatex `
  -f markdown+lists_without_preceding_blankline `
  -V CJKmainfont="Microsoft YaHei" -V CJKoptions=AutoFakeBold -V lang=zh-CN `
  -V geometry:margin=2cm -V fontsize=11pt -V linestretch=1.3
```

注意：讲稿里 `【要点】` 下一行紧接 `- ` 列表，必须加 `+lists_without_preceding_blankline`；缺 ①–④ 字形时把它们替换成 (1)(2) 或加 `newunicodechar` 映射。

## 常见坑（按症状查）

- 图太大、内容贴下边缘 → 整体上移、压帧内间距，再考虑缩图；不要为留白把图缩到看不清。
- 页面写成“分号清单” → 改完整句子或分行；页面文字禁止 `；`、`——`。
- 改了页序/标题 → 立刻 grep 讲稿和内容脚本里的旧标题/旧时间。
- Markdown 出现删除线 → 两个 `~` 被配对（如 `0.86~0.90`、`0~0.35pp`）；范围用 `–` 或“至”。
- pandoc 列表被合并 → 加 `+lists_without_preceding_blankline`。
- PPTX 保存失败 → 文件被 PowerPoint 占用，关闭或重试。
- `ModuleNotFoundError: pptx` → 换有 `pymupdf`+`pptx` 的解释器。
- 用户说“回滚” → 回上一版参数/文字，重编译重导出，再跑全部门禁。
- 输入/输出混淆 → PDF/PPTX 是生成物，永远改 `main.tex` / 内容脚本 / 讲稿。

## 多 agent 分工（可选）

Lead（页序/规则/终审）、实验（`02_experiments/`）、deck（`beamer/` + 导出）、讲稿、审计（只读）。共享任务标注 write scope；内容脚本与数字清单是唯一事实源，不手改生成物。

## 交付与安装

本 skill 是标准**目录包**：

```
academic-slide-deck/
└── SKILL.md
```

- 安装：把整个 `academic-slide-deck/` 文件夹放到 `~/.dsh/skills/`（Windows：`%USERPROFILE%\.dsh\skills\`），任意工作区可用；
- 也可放进项目的 `.dsh/skills/` 或 `.agents/skills/`（项目级优先于用户级）；
- 分享/交付：直接压缩这个文件夹，只有一个 `SKILL.md`，不会像平铺文件那样混在 skills 根目录的其他条目里；
- 修改规则只改 `SKILL.md`，不需要其他资源文件。

## 相关技能

- 不想用 LaTeX、要直接生成可编辑的 pptx：`dsh-ppt-deck`
- 讲稿要去掉 AI 味、读起来像人说话：`humanize-writing`
- 组会讲的是研究报告，先保证数字和引文对得上：`research-align`
