param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [string]$Mode = "batch",
    [string]$SessionId = "",
    [int]$Context = 0,
    [string]$Keyword = "",
    [string]$SkillType = "",
    [string]$OutputPath = "",
    [switch]$FastMode
)

$BasePath = "C:\Users\44452\.openclaw\chat-logs"
$Agents = @("main", "guaiguaixia", "pipipixia", "lelexia", "zhuizhuixia")

function Get-SessionList {
    param([string]$TargetDate)
    $sessions = @()
    foreach ($agent in $Agents) {
        $agentPath = Join-Path $BasePath $agent
        if (-not (Test-Path $agentPath)) { continue }
        $files = Get-ChildItem -Path $agentPath -Filter "$TargetDate*.jsonl" -File -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $sid = $file.Name -replace "^${TargetDate}_", "" -replace "\.jsonl$", ""
            $msgCount = if ($FastMode) { -1 } else { (Get-Content $file.FullName -TotalCount 10000 | Where-Object { $_ -match '\S' }).Count }
            $sessions += [PSCustomObject]@{
                SessionId = $sid
                Agent = $agent
                SizeKB = [math]::Round($file.Length / 1KB, 2)
                Path = $file.FullName
                MessageCount = $msgCount
            }
        }
    }
    return $sessions | Sort-Object SizeKB -Descending
}

Write-Host "=== Session List for $Date ===" -ForegroundColor Cyan
$sessions = Get-SessionList -TargetDate $Date
if ($sessions.Count -eq 0) {
    Write-Host "[FAIL] No sessions found" -ForegroundColor Red
    exit 1
}
$byAgent = $sessions | Group-Object Agent
foreach ($group in $byAgent | Sort-Object Name) {
    Write-Host "[$($group.Name)] $($group.Count) sessions" -ForegroundColor Yellow
    $group.Group | ForEach-Object {
        $msgInfo = if ($_.MessageCount -eq -1) { "(fast)" } else { "$($_.MessageCount) msgs" }
        Write-Host "  - $($_.SessionId) | $($_.SizeKB)KB | $msgInfo"
    }
}
Write-Host "=== Total: $($sessions.Count) sessions ===" -ForegroundColor Green
