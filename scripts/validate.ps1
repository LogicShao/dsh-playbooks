# 静态自检：frontmatter、目录名、内链、绝对路径、版本清单、README 索引。
# 退出码非 0 表示有错误，CI 就是靠这个拦。
[CmdletBinding()]
param()

. (Join-Path $PSScriptRoot 'lib.ps1')

$repo = Get-RepoRoot
$skillsDir = Join-Path $repo 'skills'
$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

$manifest = $null
try { $manifest = Read-Manifest $repo } catch { $errors.Add($_.Exception.Message) }

$readme = ''
$readmePath = Join-Path $repo 'README.md'
if (Test-Path -LiteralPath $readmePath) { $readme = Get-Content -LiteralPath $readmePath -Raw -Encoding utf8 }

$dirs = @(Get-ChildItem -LiteralPath $skillsDir -Directory | Sort-Object Name)
if ($dirs.Count -eq 0) { $errors.Add('skills/ 下没有技能目录') }

foreach ($d in $dirs) {
    $name = $d.Name
    $skillFile = Join-Path $d.FullName 'SKILL.md'

    if (-not (Test-Path -LiteralPath $skillFile)) { $errors.Add("$name 缺 SKILL.md"); continue }
    if (-not (Test-Path -LiteralPath (Join-Path $d.FullName 'VERSION'))) { $errors.Add("$name 缺 VERSION") }
    if (-not (Test-Path -LiteralPath (Join-Path $d.FullName 'CHANGELOG.md'))) { $warnings.Add("$name 缺 CHANGELOG.md") }

    $version = ''
    $versionPath = Join-Path $d.FullName 'VERSION'
    if (Test-Path -LiteralPath $versionPath) {
        $version = (Get-Content -LiteralPath $versionPath -Raw).Trim()
        if ($version -notmatch '^\d+\.\d+\.\d+$') { $errors.Add("$name 的 VERSION 不是语义化版本：$version") }
    }

    $text = Get-Content -LiteralPath $skillFile -Raw -Encoding utf8
    $fm = [regex]::Match($text, '(?s)^---\s*\r?\n(.*?)\r?\n---')
    if (-not $fm.Success) {
        $errors.Add("$name 的 SKILL.md 没有 frontmatter")
    }
    else {
        $fields = @{}
        foreach ($line in ($fm.Groups[1].Value -split "`r?`n")) {
            if ($line -match '^([A-Za-z][\w-]*):\s*(.*)$') { $fields[$matches[1]] = $matches[2].Trim() }
        }
        foreach ($key in 'name', 'description', 'whenToUse') {
            if (-not $fields.ContainsKey($key) -or -not $fields[$key]) { $errors.Add("$name 的 frontmatter 缺 $key") }
        }
        if ($fields['name'] -and $fields['name'] -ne $name) {
            $errors.Add("$name 的 frontmatter name=$($fields['name'])，与目录名不一致")
        }
        if ($fields['description'] -and $fields['description'].Length -gt 220) {
            $warnings.Add("$name 的 description 有 $($fields['description'].Length) 字，超过 220")
        }
    }

    # 内链：assets/、references/ 下的文件必须存在
    foreach ($m in [regex]::Matches($text, '(?:assets|references)/[\w\-.]+\.\w+')) {
        $p = Join-Path $d.FullName $m.Value
        if (-not (Test-Path -LiteralPath $p)) { $errors.Add("$name 引用了不存在的文件：$($m.Value)") }
    }

    # 绝对路径：只允许带 Program Files / $env: 的兼容分支
    foreach ($file in Get-ChildItem -LiteralPath $d.FullName -Recurse -File) {
        $body = Get-Content -LiteralPath $file.FullName -Raw -Encoding utf8
        $rel = $file.FullName.Substring($repo.Length + 1)
        foreach ($line in ($body -split "`r?`n")) {
            if ($line -match '[A-Za-z]:\\' -and $line -notmatch 'Program Files|\$env:') {
                $errors.Add("$rel 有写死的绝对路径：$($line.Trim())")
            }
        }
    }

    if ($text -notmatch '(?m)^## 相关技能') { $warnings.Add("$name 没有「相关技能」一节") }
    if ($readme -and $readme -notmatch [regex]::Escape($name)) { $warnings.Add("README 没有提到 $name") }

    if ($manifest) {
        $entry = $manifest.skills.$name
        if (-not $entry) { $errors.Add("manifest.json 里没有 $name，跑 scripts/manifest.ps1") }
        else {
            if ($entry.version -ne $version) {
                $errors.Add("$name 的 VERSION=$version，manifest 里是 $($entry.version)，跑 scripts/manifest.ps1")
            }
            $diff = Compare-SkillCopy $d.FullName $entry
            foreach ($f in $diff.Missing) { $errors.Add("$name/$f 已不在目录里，但还在 manifest 中") }
            foreach ($f in $diff.Changed) { $errors.Add("$name/$f 内容变了，manifest 过期") }
            foreach ($f in $diff.Extra) { $errors.Add("$name/$f 是新增文件，manifest 没收录") }
        }
    }
}

foreach ($w in $warnings) { Write-Host "[warn] $w" -ForegroundColor Yellow }
foreach ($e in $errors) { Write-Host "[ERROR] $e" -ForegroundColor Red }

if ($errors.Count -gt 0) {
    Write-Host "`n自检不通过：$($errors.Count) 个错误，$($warnings.Count) 个警告" -ForegroundColor Red
    exit 1
}

Write-Host "自检通过：$($dirs.Count) 个技能，$($warnings.Count) 个警告" -ForegroundColor Green
exit 0
