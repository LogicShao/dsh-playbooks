# 只读检查：目标目录里已装的副本，与仓库清单比是什么状态。
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Target
)

. (Join-Path $PSScriptRoot 'lib.ps1')

$repo = Get-RepoRoot
$manifest = Read-Manifest $repo
$base = Resolve-SkillsBase $Target

Write-Host "目标：$base`n"

$dirty = 0
foreach ($p in $manifest.skills.PSObject.Properties) {
    $name = $p.Name
    $entry = $p.Value
    $dest = Join-Path $base $name

    if (-not (Test-Path -LiteralPath $dest)) {
        Write-Host ("{0,-22} v{1,-8} 未安装" -f $name, $entry.version)
        continue
    }

    $installedVersion = ''
    $vf = Join-Path $dest 'VERSION'
    if (Test-Path -LiteralPath $vf) { $installedVersion = (Get-Content -LiteralPath $vf -Raw).Trim() }

    $diff = Compare-SkillCopy $dest $entry
    $parts = @()
    if ($installedVersion -and $installedVersion -ne $entry.version) { $parts += "版本 $installedVersion ≠ $($entry.version)" }
    if ($diff.Changed.Count) { $parts += "改动 $($diff.Changed.Count) 个文件" }
    if ($diff.Missing.Count) { $parts += "缺 $($diff.Missing.Count) 个文件" }
    if ($diff.Extra.Count) { $parts += "多 $($diff.Extra.Count) 个文件" }

    if ($parts.Count -eq 0) {
        Write-Host ("{0,-22} v{1,-8} 一致" -f $name, $entry.version) -ForegroundColor Green
    }
    else {
        Write-Host ("{0,-22} v{1,-8} {2}" -f $name, $entry.version, ($parts -join '，')) -ForegroundColor Yellow
        foreach ($f in $diff.Changed) { Write-Host "    ~ $f" -ForegroundColor DarkGray }
        foreach ($f in $diff.Missing) { Write-Host "    - $f" -ForegroundColor DarkGray }
        foreach ($f in $diff.Extra) { Write-Host "    + $f" -ForegroundColor DarkGray }
        $dirty++
    }
}

Write-Host ''
if ($dirty -eq 0) { Write-Host '全部一致' -ForegroundColor Green }
else { Write-Host "$dirty 个技能与仓库不同：本地改过就用 bump/提交回流，没改过就 install -Force 覆盖" -ForegroundColor Yellow }
