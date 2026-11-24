# 升版本：改 VERSION、往 CHANGELOG 顶部插一条、重建 manifest。
# 之后自己 commit 并打标签：git tag <skill>/v<version>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Skill,
    [ValidateSet('major', 'minor', 'patch')]
    [string]$Part = 'patch',
    [string]$Note = ''
)

. (Join-Path $PSScriptRoot 'lib.ps1')

$repo = Get-RepoRoot
$skillDir = Join-Path $repo "skills\$Skill"
if (-not (Test-Path -LiteralPath $skillDir)) { throw "没有这个技能：$Skill" }

$versionFile = Join-Path $skillDir 'VERSION'
$old = (Get-Content -LiteralPath $versionFile -Raw).Trim()
if ($old -notmatch '^(\d+)\.(\d+)\.(\d+)$') { throw "VERSION 格式不对：$old" }

$major = [int]$matches[1]; $minor = [int]$matches[2]; $patch = [int]$matches[3]
switch ($Part) {
    'major' { $major++; $minor = 0; $patch = 0 }
    'minor' { $minor++; $patch = 0 }
    'patch' { $patch++ }
}
$new = "$major.$minor.$patch"

Set-Content -LiteralPath $versionFile -Value $new -Encoding utf8 -NoNewline
Add-Content -LiteralPath $versionFile -Value "`n" -Encoding utf8

$changelogPath = Join-Path $skillDir 'CHANGELOG.md'
$today = Get-Date -Format 'yyyy-MM-dd'
$entry = "## v$new — $today`n`n- $Note`n`n"
if (Test-Path -LiteralPath $changelogPath) {
    $text = Get-Content -LiteralPath $changelogPath -Raw -Encoding utf8
    $idx = $text.IndexOf('## v')
    $text = if ($idx -ge 0) { $text.Substring(0, $idx) + $entry + $text.Substring($idx) } else { $text + "`n" + $entry }
}
else {
    $text = "# $Skill 更新记录`n`n" + $entry
}
Set-Content -LiteralPath $changelogPath -Value $text -Encoding utf8 -NoNewline

Write-Manifest $repo

Write-Host "$Skill  $old → $new" -ForegroundColor Green
Write-Host ''
Write-Host '接下来：'
Write-Host "  git add -A"
Write-Host "  git commit -m `"$Skill v$new：$Note`""
Write-Host "  git tag $Skill/v$new"
