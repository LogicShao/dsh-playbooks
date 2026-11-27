# 渲染和验收可编辑 PPTX

### 3. 渲染，然后**用眼睛看**

```python
d.save("output/deck.pptx")
d.verify()                 # 结构自检：越界、最小字号、备注
d.render("1,2,3")          # → 返回 PNG 目录，逐张看图
```

看图时按 [入口门禁](../SKILL.md#门禁) 的逐页视觉验收检查。完整交付使用 `d.render()` 渲染全部页，`d.verify()` 的小字号提示需在原文件里区分正文和图注等例外。

## 渲染命令

用 DSH 自带的 LibreOffice Kit，**不要用系统 soffice，也不要 npx**。`deck_kit` 已经封装好：

```python
out = d.render("1,2,3")    # 返回 PNG 目录
d.cleanup()                # 删掉预览目录
```

- 工具路径自动发现：先看 `DSH_NODE` / `DSH_LO_CLI`，再从 `DSH_INSTALL_DIR` / `DSH_HOME` 推导，最后退回 PATH 里的 node。都找不到时 `render()` 会直接说该设哪个环境变量。
- `--pages` 渲染子集时，PNG 按**序号**命名（`page-0001.png`），不是幻灯片编号。
- 要渲染一个不是本脚本生成的 pptx，先问出两个路径再自己拼命令行：

  ```python
  from deck_kit import find_node, find_lo_cli
  print(find_node()[0], find_lo_cli())
  ```

  ```powershell
  & "<node>" "<cli>" render --input deck.pptx --output-dir <新目录> --pages "1,2,3"
  ```

- 预览图不要留在交付目录里：`render()` 会在文件旁建 `.dsh-office-<uuid>/render/`，看完 `cleanup()`。
