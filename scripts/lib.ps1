# 共用函数。其它脚本用 . (Join-Path $PSScriptRoot 'lib.ps1') 引入。
$ErrorActionPreference = 'Stop'

function Get-RepoRoot { Split-Path -Parent $PSScriptRoot }

function Get-FileSha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-SkillFileMap([string]$SkillDir) {
    $map = [ordered]@{}
    Get-ChildItem -LiteralPath $SkillDir -Recurse -File |
        Sort-Object FullName |
        ForEach-Object {
            $rel = $_.FullName.Substring($SkillDir.Length + 1).Replace('\', '/')
            $map[$rel] = Get-FileSha256 $_.FullName
        }
    $map
}

function Read-Manifest([string]$Repo) {
    $path = Join-Path $Repo 'manifest.json'
    if (-not (Test-Path -LiteralPath $path)) { throw '缺少 manifest.json：先跑 scripts/manifest.ps1' }
    Get-Content -LiteralPath $path -Raw -Encoding utf8 | ConvertFrom-Json
}

function Write-Manifest([string]$Repo) {
    $skillsDir = Join-Path $Repo 'skills'
    $out = [ordered]@{ schema = 1; skills = [ordered]@{} }
    foreach ($d in Get-ChildItem -LiteralPath $skillsDir -Directory | Sort-Object Name) {
        $versionFile = Join-Path $d.FullName 'VERSION'
        if (-not (Test-Path -LiteralPath $versionFile)) { throw "$($d.Name) 缺 VERSION 文件" }
        $out.skills[$d.Name] = [ordered]@{
            version = (Get-Content -LiteralPath $versionFile -Raw).Trim()
            files   = Get-SkillFileMap $d.FullName
        }
    }
    $json = $out | ConvertTo-Json -Depth 8
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path $Repo 'manifest.json'), $json + "`n", $utf8)
}

function Resolve-SkillsBase([string]$Target) {
    if ($Target -eq 'profile') {
        if (-not $env:DSH_HOME) { throw '没有 DSH_HOME，无法定位 profile 目录' }
        return (Join-Path $env:DSH_HOME 'skills')
    }
    $full = (Resolve-Path -LiteralPath $Target).Path
    Join-Path $full '.dsh\skills'
}

# 对比已装副本与清单，返回 @{ Missing=@(); Changed=@(); Extra=@() }
function Compare-SkillCopy([string]$Dest, $Entry) {
    $missing = @(); $changed = @()
    foreach ($f in $Entry.files.PSObject.Properties) {
        $p = Join-Path $Dest ($f.Name -replace '/', '\')
        if (-not (Test-Path -LiteralPath $p)) { $missing += $f.Name; continue }
        if ((Get-FileSha256 $p) -ne $f.Value) { $changed += $f.Name }
    }
    $known = @($Entry.files.PSObject.Properties.Name)
    $installed = Get-SkillFileMap $Dest
    $extra = @($installed.Keys | Where-Object { $_ -notin $known })
    [pscustomobject]@{ Missing = $missing; Changed = $changed; Extra = $extra }
}
