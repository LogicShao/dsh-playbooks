# 导出和验收 Beamer 幻灯片

## 编译和检查日志

- **编译**：`xelatex -interaction=nonstopmode main.tex` 跑两遍；0 error、Overfull/Underfull = 0。

```powershell
Select-String -Path main.log -Pattern '^(?:!|Overfull|Underfull)'
```

XeLaTeX 退出码为 0，且上面的检查无输出，再导出 PPTX。

## 导出 PDF + PPTX

PDF 复制到 `05_交付/deck.pdf`；PPTX 输出到 `05_交付/deck.pptx`；讲稿 PDF 也放这里。PPTX 转换要用同时装了 `pymupdf` 和 `python-pptx` 的解释器，先确认再动手：

```powershell
& "$py" -c "import pymupdf, pptx; print('ok')"
```

在转换脚本旁放置 [备注解析器](../assets/beamer_notes.py)。先运行 `& "$py" beamer_notes.py main.tex main.pdf`，再在下面的示例前加 `from beamer_notes import parse_notes_from_tex`。示例须由同时装有 Pillow 的解释器执行。

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

若用户只给现有 Beamer PDF，先确认是否要备注。若不需要，将复制出的示例中的 `notes = parse_notes_from_tex("main.tex")` 改为 `notes = []`，并将 `main.pdf` 替换为现有文件。如果要备注，先补齐 Beamer 源稿再按带备注路线转换。

## 验收和清理

```powershell
& "$py" beamer_notes.py main.tex main.pdf deck.pptx
New-Item -ItemType Directory -Force -Path preview/academic | Out-Null
pdftoppm -png -r 144 main.pdf preview/academic/page
```

仅转换 PDF 且约定无备注时，在第一条命令中用 `--pdf-only` 代替 `main.tex`。按[入口门禁](../SKILL.md#门禁)查看全部 PNG。

底部留白速测：2x 渲染每页，找最低非白行，`margin_mm = (h-1-last_row)/2*0.3528`；低于阈值就报页码。

在 PNG 图像工具里沿每页全宽找最低非白像素行，记下图像高度 `h` 与该行从 0 起算的 `last_row`，代入上式，合格页底部至少 10mm（11mm 更稳）。不足时先整体上移或压间距，再缩图 2–4mm。

交付前列出专用目录内容，对照[制作配方的交付树](create-beamer-deck.md)。从预览和编译目录清除 `_check_*.png`、`.aux/.log/.nav` 等临时文件。

- PPTX 保存失败 → 文件被 PowerPoint 占用，关闭或重试。
- `ModuleNotFoundError: pptx` → 换有 `pymupdf`+`pptx` 的解释器。
