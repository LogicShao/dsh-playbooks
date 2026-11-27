# 版式数值验收

「编译 0 错误」不等于「版式没问题」。空白页、半空页、栏底断层都不会报错。**必须逐页量。**

## 一、先把每页渲染成图

```powershell
# pdftoppm 随 MiKTeX / poppler 安装，位置因机器而异：先在 PATH 里找，找不到再试常见目录
$pdftoppm = (Get-Command pdftoppm -ErrorAction SilentlyContinue).Source
if (-not $pdftoppm) {
  $pdftoppm = (Get-ChildItem "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdftoppm.exe",
                            "$env:ProgramFiles\MiKTeX\miktex\bin\x64\pdftoppm.exe" `
                            -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}
if (-not $pdftoppm) { throw "找不到 pdftoppm：装 MiKTeX 或 poppler，或把它的目录加进 PATH" }

cd <报告目录>
Remove-Item preview\*.png -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path preview | Out-Null
& $pdftoppm -png -r 70 报告.pdf preview/p
```

70 dpi 够用，量的是版面占位不是清晰度。

## 二、量填充率与栏内断层

```python
from PIL import Image
import numpy as np, glob

pages = sorted(glob.glob('preview/p-*.png'), key=lambda name: int(name.rsplit('-', 1)[1][:-4]))
if not pages:
    raise SystemExit("没找到预览 PNG")
for number, f in enumerate(pages, 1):
    im = np.array(Image.open(f).convert('L'))
    h, w = im.shape
    # 裁掉页眉页脚与左右白边，只留版心
    b = im[int(h*0.05):int(h*0.93), int(w*0.055):int(w*0.945)]
    H, W = b.shape
    fill, gaps = [], []
    for c in (b[:, :W//2], b[:, W//2:]):
        ink = (c < 200).sum(axis=1) > 2
        nz = np.nonzero(ink)[0]
        fill.append(nz[-1]/H*100 if len(nz) else 0)
        # 栏内最大连续空白
        run = mx = 0
        for i in range(nz[0]+1, nz[-1]) if len(nz) else ():
            if not ink[i]:
                run += 1; mx = max(mx, run)
            else:
                run = 0
        gaps.append(mx/H*100)
    tag = ''
    fill_limit = 60 if number == len(pages) else 75
    if max(fill) < fill_limit: tag += ' << 空'
    if max(gaps) > 12: tag += ' << 大空白'
    if abs(fill[0] - fill[1]) > 10: tag += ' << 双栏差'
    print('%s L%.0f%% R%.0f%% gap%.0f/%.0f%%%s' % (number, fill[0], fill[1], gaps[0], gaps[1], tag))
```

输出形如：

```
1 L96% R100% gap3/3%
2 L100% R100% gap2/3%
3 L98%  R100% gap8/8%
4 L100% R100% gap3/4%
5 L100% R100% gap2/4%
6 L100% R100% gap2/4%
7 L95%  R95%  gap2/2%
```

## 三、阈值

| 指标 | 合格 | 处理 |
|---|---|---|
| 单页填充率 | ≥ 90% | 75–90% 看情况优化，< 75% 必修 |
| 页内最大连续空白 | ≤ 12% | 超过说明有断层，找 `\needspace` 或浮动体 |
| 末页填充率 | ≥ 60% | < 60% 通常是参考文献溢出，压版式而不是加内容 |
| 双栏页左右差 | ≤ 10 个百分点 | 差太多说明一侧有浮动体挤压 |

末页用 60% 下限。逐页复查脚本标出的页码，修订后重新渲染并运行测量。

## 四、六种典型塌法

### 1. 双栏模式下用 `[H]` 放算法体

```
! LaTeX Error: [H] in two columns mode is not allowed for algorithms.
```

改用 `algorithm` + `algpseudocode` 浮动体，位置写 `[tbp]`。

### 2. `\needspace` 写在段落中间，强制断栏

现象：某页栏底空出两成，下半页从新的一段开始。

原因：`\needspace` 遇到当前段落剩余高度不够，会直接断栏，把整段推到下一栏。

处理：把守卫值调小（`4\baselineskip` → `2.5\baselineskip`），或者移到段落之间而不是段落中间。

### 3. `figure*` / `table*` 在页中间插入，把前一页截断

现象：浮动体所在页的上一页，栏底突然空一块。

原因：跨栏浮动体在遇到的位置插入分页惩罚，前面的正文被迫提前结束。

处理：把浮动体挪到小节边界，别放在段中间。

### 4. 文末残留 `\vspace` + `\Needspace`

现象：多出一个几乎空白的尾页，里面什么都没有。

原因：`\end{document}` 之前的 `\Needspace*{4\baselineskip}` 和 `\vspace{1.2em}` 会在最后一页制造新页。

处理：删掉这两个东西。

### 5. 参考文献溢出到新页

现象：正文刚好排满末页，参考文献挤出一页，新页只有三四行。

处理顺序（从轻到重）：

1. 缩短作者列表：`A, B, C, D, E, F.` → `A 等.`
2. 参考文献字号 `\small` → `\footnotesize`
3. 调 `\itemsep`：`0.15em` → `0.08em`
4. 微调页边距：`top=1.78cm` → `1.72cm`
5. 调行距：`\linespread{1.07}` → `1.055`

先试第 1 条，通常就够了。第 4、5 条改的是全局观感，留到最后。

### 6. 段落长度全部等长

现象：每段都是四五句，读起来像流水线。

检查：统计正文段落汉字数。健康的分布是「最短十几字、最长一百五十字以上、平均七十左右」，如果最大最小差距不到两倍，说明段落是被均匀切出来的。

处理：合并短段、拆开长段，允许一句话成段。

## 五、文字层机械检查

若用户确认了相应文字及格式限制，先运行机械检查。下面是按字面匹配的快速筛查，可定位待人工确认的内容。

```powershell
$t = Get-Content 报告.tex -Raw
foreach($p in @('；','——','\rule','itemize','enumerate')){
  $c = ([regex]::Matches($t,[regex]::Escape($p))).Count
  if($c -gt 0){ "违规 [$p] ×$c" }
}
"引用 $( ([regex]::Matches($t,'\\cite\{')).Count ) | 文献 $( ([regex]::Matches($t,'\\bibitem')).Count )"
```

更具体的环境、词表和统计见下一段。只将本报告约定的禁用项计为违规。

```powershell
$t = Get-Content 报告.tex -Raw

# 禁用标点与格式
foreach($p in @('；','——','\rule','begin{itemize}','begin{enumerate}')){
  $c = ([regex]::Matches($t,[regex]::Escape($p))).Count
  if($c -gt 0){ "违规 [$p] ×$c" }
}

# AI 味词表
foreach($p in @('值得注意','值得一提','综上所述','总而言之','换句话说','显而易见','众所周知','需要注意的是')){
  $c = ([regex]::Matches($t,[regex]::Escape($p))).Count
  if($c -gt 0){ "AI 味 [$p] ×$c" }
}

# 统计
"引用 $( ([regex]::Matches($t,'\\cite\{')).Count ) 处"
"文献 $( ([regex]::Matches($t,'\\bibitem')).Count ) 条"
"表 $( ([regex]::Matches($t,'begin\{table')).Count ) | 图 $( ([regex]::Matches($t,'begin\{figure')).Count )"
"汉字约 $( ([regex]::Matches($t,'[\u4e00-\u9fa5]')).Count ) 字"
```

编译后查日志：

```powershell
$log = Get-Content 报告.log -Raw
"错误 " + ([regex]::Matches($log,'(?m)^!')).Count
"溢出 " + ([regex]::Matches($log,'Overfull \\hbox')).Count
"未定义引用 " + ([regex]::Matches($log,'Reference .* undefined')).Count
"未定义文献 " + ([regex]::Matches($log,'Citation .* undefined')).Count
"缺字 " + ([regex]::Matches($log,'Missing character')).Count
```

**缺字必须为 0。** 中文字体缺字不会报错，只会显示成空白或方框，扫一眼容易漏。

## 六、结构改动的安全做法

改章节顺序、移动浮动体、批量替换这类操作，**先备份再改**。

改浮动体时，比对前后图表数量、标题和引用，防止误删仍能编译的图表。

改完先做结构完整性检查：

```powershell
$t = Get-Content 报告.tex -Raw
"begin{table}  $( ([regex]::Matches($t,'begin\{table')).Count )  / end{table}  $( ([regex]::Matches($t,'end\{table')).Count )"
"begin{figure} $( ([regex]::Matches($t,'begin\{figure')).Count ) / end{figure} $( ([regex]::Matches($t,'end\{figure')).Count )"
"begin{tabular} $( ([regex]::Matches($t,'begin\{tabular')).Count ) / end{tabular} $( ([regex]::Matches($t,'end\{tabular')).Count )"
```

begin / end 数量必须相等。再做一次重复行扫描，防止字符串替换把同一段插了两遍——这种错误编译不报，但读者会看到重复段落。
