# read-chatlogs.ps1
# Function: Read chat-logs for all agents on specified date, output formatted conversations
# Usage: powershell -ExecutionPolicy Bypass -File "read-chatlogs.ps1" -Date "2026-03-21"

param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [string]$OutputFormat = "text"
)

$BasePath = "C:\Users\44452\.openclaw\chat-logs"
$Agents = @("guaiguaixia", "lelexia", "main", "pipipixia", "zhuizhuixia")

Write-Host "=== Reading Date: $Date ==="
Write-Host ""

$allSessions = @()
foreach ($agent in $Agents) {
    $agentPath = Join-Path $BasePath $agent
    if (Test-Path $agentPath) {
        $files = Get-ChildItem $agentPath -Filter "*.jsonl" -ErrorAction SilentlyContinue | 
                 Where-Object { $_.Name -like "*${Date}*" }
        
        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            $allSessions += @{
                Agent = $agent
                File = $file.Name
                Path = $file.FullName
                Content = $content
            }
        }
    }
}

if ($allSessions.Count -eq 0) {
    Write-Host "[WARN] No chat-logs found for $Date"
    Write-Host ""
    Write-Host "[INFO] Fallback to sessions directory..."
    Write-Host ""
    
    $sessionsBase = "C:\Users\44452\.openclaw\agents"
    $cutoff = [DateTime]::ParseExact($Date, "yyyy-MM-dd", $null).Date
    $cutoffEnd = $cutoff.AddDays(1)
    
    foreach ($agent in $Agents) {
        $sessionsPath = Join-Path $sessionsBase "$agent\sessions"
        if (Test-Path $sessionsPath) {
            $sessionFiles = Get-ChildItem $sessionsPath -Filter "*.jsonl" | 
                           Where-Object { $_.LastWriteTime -ge $cutoff -and $_.LastWriteTime -lt $cutoffEnd }
            foreach ($file in $sessionFiles) {
                Write-Host "=== Agent: $agent | Session: $($file.Name) ==="
                Get-Content $file.FullName -Encoding UTF8 | Select-Object -First 50
                Write-Host ""
            }
        }
    }
} else {
    Write-Host "[INFO] Found $($allSessions.Count) session files"
    Write-Host ""
    
    foreach ($session in $allSessions) {
        Write-Host "=== Agent: $($session.Agent) | File: $($session.File) ==="
        
        $session.Content -split "`n" | ForEach-Object {
            if ($_ -and $_.Trim()) {
                try {
                    $entry = $_ | ConvertFrom-Json
                    if ($entry.type -eq "message" -and $entry.message) {
                        $role = $entry.message.role
                        $timestamp = $entry.timestamp
                        $text = ""
                        
                        if ($entry.message.content -is [array]) {
                            $text = ($entry.message.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text }) -join ""
                        } elseif ($entry.message.content -is [string]) {
                            $text = $entry.message.content
                        }
                        
                        if ($text -and $role) {
                            $timeStr = if ($timestamp) { 
                                [DateTime]::FromUnixTimeMilliseconds($timestamp).ToString("HH:mm:ss") 
                            } else { "----" }
                            Write-Host "[$timeStr] $role`: $text"
                        }
                    }
                } catch {
                    # Ignore parse errors
                }
            }
        }
        Write-Host ""
    }
}

Write-Host ""
Write-Host "=== Reading Complete ==="
