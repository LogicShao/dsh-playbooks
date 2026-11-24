# 根据 skills/*/VERSION 与文件内容重建 manifest.json。
# 任何 skill 内容改动（包括改错字）都要重跑一次，否则 validate 会报清单过期。
[CmdletBinding()]
param()

. (Join-Path $PSScriptRoot 'lib.ps1')

$repo = Get-RepoRoot
Write-Manifest $repo

$manifest = Read-Manifest $repo
foreach ($p in $manifest.skills.PSObject.Properties) {
    $count = @($p.Value.files.PSObject.Properties).Count
    '{0,-22} v{1,-8} {2} 个文件' -f $p.Name, $p.Value.version, $count
}
