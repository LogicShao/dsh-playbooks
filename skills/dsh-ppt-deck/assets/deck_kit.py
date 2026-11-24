"""deck_kit —— 汇报级 PPT 的最小工具箱（python-pptx）。

配合同目录上级的 SKILL.md 使用。典型用法：

    from deck_kit import *

    d = Deck(title="项目汇报", author="邵逸帆")
    s = d.blank()
    header(s, "一句话结论当标题")
    body(s, 0.9, 1.8, "正文一条，不超过十二字")
    page_no(s, 1, 8)

    d.save("output/deck-v1.pptx")
    print(d.verify())        # 结构自检
    d.render("1,2")          # 渲染成 PNG，肉眼看
    d.cleanup()              # 删掉预览目录

规则见 SKILL.md：一页一张图、对象数 2–6、正文 ≥18pt、不放装饰小字。

渲染依赖 node 和 DSH 自带的 LibreOffice Kit CLI，路径自动发现；
找不到时可用环境变量 DSH_NODE / DSH_LO_CLI / DSH_INSTALL_DIR 指定。
"""

import os
import shutil
import subprocess
import uuid
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# ---------------------------------------------------------------- 设计参数

SLIDE_W, SLIDE_H = 13.333, 7.5
MARGIN = 0.95
CONTENT_W = SLIDE_W - 2 * MARGIN

FONT_SANS = "Microsoft YaHei"     # 正文 / 标题
FONT_SERIF = "华文中宋"            # 封面 / 尾页

INK = RGBColor(0x10, 0x14, 0x18)
BODY = RGBColor(0x3D, 0x46, 0x53)
SUBTLE = RGBColor(0x8A, 0x94, 0xA3)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
RULE = RGBColor(0xE3, 0xE7, 0xEE)
PANEL = RGBColor(0xF7, 0xF9, 0xFC)
BAD = RGBColor(0xB4, 0x23, 0x18)
GOOD = RGBColor(0x0E, 0x9F, 0x6E)

# 页面标题 24–34（页内图多则取小）；正文下限 18
SIZE_COVER, SIZE_TITLE, SIZE_SUB, SIZE_BODY, SIZE_MIN = 48, 28, 20, 18, 12

# ---------------------------------------------------------------- 运行环境
#
# 渲染要两样外部工具：node 和 DSH 自带的 LibreOffice Kit CLI。路径不写死，
# 按下面的顺序发现；都不成立时 render() 会说明该设哪个环境变量。
#   1. DSH_NODE / DSH_LO_CLI 显式指定
#   2. DSH_INSTALL_DIR / DSH_NODE_EXECUTABLE / DSH_HOME 推导
#   3. PATH 里的 node

_LO_CLI_REL = ("@deepseek-ai", "libreoffice-kit", "lib", "cli.js")


def _unpacked(path):
    """Desktop 把 node_modules 打进 app.asar，可执行脚本必须取 app.asar.unpacked 的那份。"""
    s = str(path)
    return Path(s.replace("app.asar", "app.asar.unpacked", 1)) if "app.asar" in s else Path(s)


def _resources_dir():
    inst = os.environ.get("DSH_INSTALL_DIR")
    if not inst:
        return None
    for parent in [Path(inst), *Path(inst).parents]:
        if parent.name.lower() == "app.asar":
            return parent.parent
        if parent.name.lower() == "resources":
            return parent
    return None


def _lo_cli_candidates():
    if os.environ.get("DSH_LO_CLI"):
        yield Path(os.environ["DSH_LO_CLI"])
    inst = os.environ.get("DSH_INSTALL_DIR")
    if inst:
        modules = Path(inst).parent.parent                     # .../node_modules
        yield _unpacked(modules.joinpath(*_LO_CLI_REL))
        yield modules.joinpath(*_LO_CLI_REL)
    res = _resources_dir()
    if res:
        yield res / "app.asar.unpacked" / "dsh" / "node_modules" / Path(*_LO_CLI_REL)


def _node_candidates():
    """(路径, 是否要 ELECTRON_RUN_AS_NODE=1)。优先 DSH 自带运行时，PATH 里的 node 排后面。"""
    if os.environ.get("DSH_NODE"):
        yield Path(os.environ["DSH_NODE"]), False
    home = os.environ.get("DSH_HOME")
    if home:
        yield (Path(home) / "dsh-runtimes" / "dsh-primary-runtime" / "dependencies"
               / "node" / "bin" / "node.exe"), False
    res = _resources_dir()
    if res:
        yield (res / "runtime" / "primary-runtime" / "dependencies"
               / "node" / "bin" / "node.exe"), False
    which = shutil.which("node") or shutil.which("node.exe")
    if which:
        yield Path(which), False
    if os.environ.get("DSH_NODE_EXECUTABLE"):
        yield Path(os.environ["DSH_NODE_EXECUTABLE"]), True      # Electron 以 node 身份跑


def find_node():
    for path, electron in _node_candidates():
        if path.is_file():
            return path, electron
    return None, False


def find_lo_cli():
    for path in _lo_cli_candidates():
        if path.is_file():
            return path
    return None

EMU = 914400.0


# ---------------------------------------------------------------- 文本

def _set_ea(run, name):
    """中文必须同时写 a:ea，否则回落到默认字体。"""
    latin = run._r.get_or_add_rPr().find(qn("a:latin"))
    if latin is not None:
        latin.addnext(latin.makeelement(qn("a:ea"), {"typeface": name}))


def style_run(run, size=SIZE_BODY, color=BODY, bold=False, font=FONT_SANS, spc=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    _set_ea(run, font)
    if spc is not None:
        run._r.get_or_add_rPr().set("spc", str(int(spc)))


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, 0)
    return tf


def add_run(p, text, **kw):
    r = p.add_run()
    r.text = text
    style_run(r, **kw)
    return r


def para(tf, text=None, *, size=SIZE_BODY, color=BODY, bold=False, spacing=1.25,
         before=0, after=0, spc=None, align=PP_ALIGN.LEFT, font=FONT_SANS, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.line_spacing = spacing
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    if text:
        add_run(p, text, size=size, color=color, bold=bold, font=font, spc=spc)
    return p


def body(slide, x, y, text, *, w=None, size=SIZE_BODY, color=BODY, bold=False,
         h=None, spacing=1.4):
    """一个正文块（单段）。"""
    w = w if w is not None else CONTENT_W - (x - MARGIN)
    h = h if h is not None else size / 72.0 * 2.2
    tf = textbox(slide, x, y, w, h)
    para(tf, text, size=size, color=color, bold=bold, spacing=spacing, first=True)
    return tf


# ---------------------------------------------------------------- 形状

def strip_style(shape):
    """删掉 <p:style>：只设 shadow.inherit=False 在 LibreOffice/WPS 下仍会带阴影。"""
    style = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)
    try:
        shape.shadow.inherit = False
    except Exception:
        pass


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0,
         shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    strip_style(s)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if s.has_text_frame:
        s.text_frame.word_wrap = True
    return s


def panel(slide, x, y, w, h, *, fill=None, line=RULE, radius=0.08, text=None,
          size=SIZE_BODY, color=INK, bold=False):
    """流程图里的圆角方框，可直接带一行文字。"""
    s = rect(slide, x, y, w, h,
             fill=fill if fill is not None else RGBColor(0xFF, 0xFF, 0xFF),
             line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=radius)
    if text:
        tf = s.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(tf, side, Inches(0.06))
        para(tf, text, size=size, color=color, bold=bold,
             align=PP_ALIGN.CENTER, spacing=1.15, first=True)
    return s


def arrow(slide, x1, y1, x2, y2, color=BODY, width=1.5):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                   Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"),
                             {"type": "triangle", "w": "med", "len": "med"}))
    return c


# ---------------------------------------------------------------- 页面骨架

def header(slide, title, *, size=SIZE_TITLE, rule_w=None, rule_color=None, y=0.40):
    """左上标题 + 与标题等宽的淡色下划线。整套稿只用这一个骨架。"""
    tf = textbox(slide, MARGIN, y, CONTENT_W, size / 72.0 * 1.5)
    para(tf, title, size=size, color=INK, bold=True, spacing=1.1, first=True)
    if rule_w is None:
        rule_w = min(max(len(title) * size / 72.0 * 0.98, 1.2), CONTENT_W)
    rect(slide, MARGIN - 0.05, y + size / 72.0 * 1.55, rule_w, 0.052,
         fill=rule_color or ACCENT)
    return rule_w


def page_no(slide, idx, total, *, y=7.02):
    tf = textbox(slide, SLIDE_W - MARGIN - 1.4, y, 1.4, 0.28)
    para(tf, f"{idx} / {total}", size=SIZE_MIN, color=SUBTLE,
         align=PP_ALIGN.RIGHT, first=True)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def cover(slide, title, subtitle=None, meta=None, date=None):
    """封面：衬线大字居中。"""
    rect(slide, 0, 0, 0.26, SLIDE_H, fill=ACCENT)
    tf = textbox(slide, 1.15, 2.35, CONTENT_W - 0.4, 1.6)
    para(tf, title, size=SIZE_COVER, color=INK, bold=True, spacing=1.15,
         font=FONT_SERIF, first=True)
    y = 2.35 + SIZE_COVER / 72.0 * 1.6
    if subtitle:
        body(slide, 1.15, y + 0.15, subtitle, size=24, color=ACCENT, bold=True)
    tail = "　".join(t for t in (meta, date) if t)
    if tail:
        body(slide, 1.15, y + 0.75, tail, size=SIZE_MIN, color=SUBTLE)


# ---------------------------------------------------------------- 文档对象

class Deck:
    def __init__(self, title="", author="", width=SLIDE_W, height=SLIDE_H):
        self.prs = Presentation()
        self.prs.slide_width = Inches(width)
        self.prs.slide_height = Inches(height)
        self.title, self.author = title, author
        self.width, self.height = width, height
        self._path = None
        self._previews = []

    # -- 基础 --

    def blank(self):
        return self.prs.slides.add_slide(self.prs.slide_layouts[6])

    @property
    def slides(self):
        return self.prs.slides

    def save(self, path):
        self.prs.core_properties.title = self.title
        self.prs.core_properties.author = self.author
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.prs.save(path)
        self._path = path
        return path

    # -- 自检 --

    def verify(self, verbose=True):
        """结构自检：越界、最小字号、每页对象数、备注。返回问题列表。"""
        prs = Presentation(self._path) if self._path else self.prs
        issues, sizes = [], []
        for i, sl in enumerate(prs.slides, 1):
            for sh in sl.shapes:
                if None in (sh.left, sh.top):
                    continue
                r = (sh.left + sh.width) / EMU
                b = (sh.top + sh.height) / EMU
                if r > self.width + 0.02:
                    issues.append(f"p{i} 越界右侧 {r:.2f}in")
                if b > self.height + 0.02:
                    issues.append(f"p{i} 越界底部 {b:.2f}in")
                if not sh.has_text_frame:
                    continue
                for p in sh.text_frame.paragraphs:
                    for run in p.runs:
                        if run.font.size:
                            sizes.append(run.font.size.pt)
            n = len(sl.shapes)
            if n > 10:
                issues.append(f"p{i} 对象数 {n} > 10，可能在用形状凑版面")
            if n < 2:
                issues.append(f"p{i} 只有 {n} 个对象")
            if not sl.has_notes_slide or not sl.notes_slide.notes_text_frame.text.strip():
                issues.append(f"p{i} 没有演讲者备注")
        if sizes and min(sizes) < SIZE_BODY:
            small = sorted({s for s in sizes if s < SIZE_BODY})
            if verbose:
                print(f"[提示] 存在 {small} pt 文字；只有图注/图例/页码可以用小字")
        if verbose:
            print(f"[verify] {len(prs.slides)} 页，问题 {len(issues)} 条")
            for x in issues:
                print("   -", x)
        return issues

    # -- 渲染 --

    def render(self, pages="all"):
        """用 LibreOffice Kit 渲染成 PNG，返回目录。看完记得 cleanup()。"""
        if not self._path:
            raise RuntimeError("先 save() 再 render()")
        (node, electron), lo_cli = find_node(), find_lo_cli()
        if node is None or lo_cli is None:
            missing = "node" if node is None else "LibreOffice Kit CLI"
            raise RuntimeError(
                f"找不到 {missing}。下面三种方式设一种即可：\n"
                "  - DSH_NODE 指向 node.exe，DSH_LO_CLI 指向 libreoffice-kit/lib/cli.js\n"
                "  - DSH_INSTALL_DIR 指向 DSH 安装目录，脚本会据此推导\n"
                "  - 把 node 放进 PATH")
        parent = os.path.join(os.path.dirname(os.path.abspath(self._path)),
                              f".dsh-office-{uuid.uuid4().hex}")
        os.makedirs(parent, exist_ok=True)
        out = os.path.join(parent, "render")
        cmd = [str(node), str(lo_cli), "render", "--input", self._path, "--output-dir", out]
        if pages and pages != "all":
            cmd += ["--pages", str(pages)]
        env = dict(os.environ)
        if electron:
            env["ELECTRON_RUN_AS_NODE"] = "1"
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env)
        if proc.returncode != 0:
            raise RuntimeError(f"LibreOffice Kit 渲染失败（exit {proc.returncode}）：\n"
                               f"{(proc.stderr or proc.stdout)[-1500:]}")
        self._previews.append(parent)
        print(f"[render] {out}")
        if pages and pages != "all":
            print("[render] 指定 --pages 时 PNG 按序号命名，不是幻灯片编号")
        return out

    def cleanup(self):
        import shutil
        for d in self._previews:
            shutil.rmtree(d, ignore_errors=True)
        self._previews.clear()


__all__ = [
    "Deck", "header", "body", "page_no", "notes", "cover",
    "rect", "panel", "arrow", "textbox", "para", "add_run", "style_run", "strip_style",
    "SLIDE_W", "SLIDE_H", "MARGIN", "CONTENT_W",
    "INK", "BODY", "SUBTLE", "ACCENT", "RULE", "PANEL", "BAD", "GOOD",
    "FONT_SANS", "FONT_SERIF",
    "SIZE_COVER", "SIZE_TITLE", "SIZE_SUB", "SIZE_BODY", "SIZE_MIN",
    "find_node", "find_lo_cli",
]
