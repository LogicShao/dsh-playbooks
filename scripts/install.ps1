# 把技能复制到项目的 .dsh/skills/，或 profile 的 skills/。
# 默认不覆盖已经改过的副本；-Force 才覆盖，-Backup 会先把旧副本挪走。
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Target,                      # 项目目录；写 profile 表示装到全局
    [string[]]$Skill = @('all'),
    [switch]$Force,
    [switch]$Backup,
    [switch]$DryRun
)

. (Join-Path $PSScriptRoot 'lib.ps1')

$repo = Get-RepoRoot
$manifest = Read-Manifest $repo
$base = Resolve-SkillsBase $Target
$names = if ($Skill -contains 'all') { @($manifest.skills.PSObject.Properties.Name) } else { @($Skill) }

Write-Host "目标：$base"
if ($DryRun) { Write-Host '（DryRun：只报告，不写文件）' }
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $base | Out-Null }

$added = 0; $same = 0; $updated = 0; $blocked = 0

foreach ($name in $names) {
    $entry = $manifest.skills.$name
    if (-not $entry) { Write-Warning "manifest 里没有 $name"; $blocked++; continue }

    $src = Join-Path $repo "skills\$name"
    $dest = Join-Path $base $name

    if (-not (Test-Path -LiteralPath $dest)) {
        if ($DryRun) { Write-Host "  [新增] $name v$($entry.version)"; continue }
        Copy-Item -LiteralPath $src -Destination $base -Recurse -Force
        Write-Host "  [新增] $name v$($entry.version)" -ForegroundColor Green
        $added++
        continue
    }

    $diff = Compare-SkillCopy $dest $entry
    if ($diff.Missing.Count -eq 0 -and $diff.Changed.Count -eq 0 -and $diff.Extra.Count -eq 0) {
        Write-Host "  [一致] $name v$($entry.version)" -ForegroundColor DarkGray
        $same++
        continue
    }

    $detail = @()
    if ($diff.Changed.Count) { $detail += "已修改 $($diff.Changed.Count)" }
    if ($diff.Missing.Count) { $detail += "缺文件 $($diff.Missing.Count)" }
    if ($diff.Extra.Count) { $detail += "多文件 $($diff.Extra.Count)" }

    if (-not $Force) {
        Write-Host "  [跳过] $name（$($detail -join '，')）；要覆盖加 -Force" -ForegroundColor Yellow
        $blocked++
        continue
    }

    if ($DryRun) { Write-Host "  [覆盖] $name v$($entry.version)（$($detail -join '，')）"; continue }

    if ($Backup) {
        $bak = "$dest.bak-" + (Get-Date -Format 'yyyyMMdd-HHmmss')
        Move-Item -LiteralPath $dest -Destination $bak
        Write-Host "  备份 → $bak" -ForegroundColor DarkGray
    }
    else {
        Remove-Item -LiteralPath $dest -Recurse -Force
    }
    Copy-Item -LiteralPath $src -Destination $base -Recurse -Force
    Write-Host "  [覆盖] $name v$($entry.version)（$($detail -join '，')）" -ForegroundColor Green
    $updated++
}

Write-Host ''
Write-Host "新增 $added | 一致 $same | 覆盖 $updated | 跳过 $blocked"
if ($blocked -gt 0 -and -not $Force) {
    Write-Host '跳过的副本可能有本地改动：先 status.ps1 看清楚，再决定 -Force 还是手工合并。' -ForegroundColor Yellow
}
