# 写逐页讲稿和导出 PDF

- **讲稿**：每页三段；【口播】按 240 汉字/分钟，总量≈时长；公式用 `$...$`；数字与清单一致。

合计每页实测口播时长。改过页序、标题或时长后，在讲稿和内容脚本中搜索被替换的标题和旧时长，确认无命中。验收阈值见[入口门禁](../SKILL.md#门禁)。

## 讲稿可选导出 PDF

```powershell
pandoc "讲稿.md" -o "05_交付/讲稿.pdf" --pdf-engine=xelatex `
  -f markdown+lists_without_preceding_blankline `
  -V CJKmainfont="Microsoft YaHei" -V CJKoptions=AutoFakeBold -V lang=zh-CN `
  -V geometry:margin=2cm -V fontsize=11pt -V linestretch=1.3
```

注意：讲稿里 `【要点】` 下一行紧接 `- ` 列表，必须加 `+lists_without_preceding_blankline`；缺 ①–④ 字形时把它们替换成 (1)(2) 或加 `newunicodechar` 映射。

仅在交付契约要求 PDF 讲稿时运行上述命令。

- Markdown 出现删除线 → 两个 `~` 被配对（如 `0.86~0.90`、`0~0.35pp`）；范围用 `–` 或“至”。
- pandoc 列表被合并 → 加 `+lists_without_preceding_blankline`。
