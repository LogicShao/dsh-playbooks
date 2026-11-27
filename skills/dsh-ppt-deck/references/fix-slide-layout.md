# 修复 PowerPoint 版式问题

遇到阴影、中文字体或标题遮挡时，按现象选对应段落。修复后重新渲染受影响的页。

### 1. 形状自带主题阴影

`shape.shadow.inherit = False` 只加一个空 effectLst，PowerPoint 听话，但
LibreOffice / WPS 仍按 `<p:style>/@effectRef` 补阴影。**必须删掉整个 `p:style`**：

```python
style = shape._element.find(qn("p:style"))
if style is not None:
    shape._element.remove(style)
```

### 2. 中文字体不生效

只设 `run.font.name` 只会写 `a:latin`，中文回落到默认字体。要同时写 `a:ea`：

```python
latin = run._r.get_or_add_rPr().find(qn("a:latin"))
latin.addnext(latin.makeelement(qn("a:ea"), {"typeface": name}))
```

### 4. 标题和副标题撞在一起

手排最常见的事故：标题和副标题同 y 起排，直接叠字；长标题换行后穿过下划线。
写完先量宽度：`标题字数 × 字号pt / 72` 英寸，超过版心就缩字号或换行。
