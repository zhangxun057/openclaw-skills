# read-session-detail.ps1
# Function: 精读回查 - 获取指定 session 的详细内容或关键词上下文
# Usage:
#   完整读取: powershell -File "read-session-detail.ps1" -Date "2026-03-23" -SessionId "abc123"
#   关键词搜索: powershell -File "read-session-detail.ps1" -Date "2026-03-23" -SessionId "abc123" -Keyword "心跳" -Context 5
#   行号范围: powershell -File "read-session-detail.ps1" -Date "2026-03-23" -SessionId "abc123" -StartLine 10 -EndLine 30

param(
    [Parameter(Mandatory=$true)]
    [string]$Date,
    
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [string]$Keyword = "",
    [int]$Context = 5,
    [int]$StartLine = 0,
    [int]$EndLine = 0,
    [switch]$Raw,          # 输出原始 JSON 而非格式化文本
    [switch]$Stats         # 仅显示统计信息
)

$BasePath = "C:\Users\44452\.openclaw\chat-logs"

# Find the session file
$file = Get-ChildItem -Path $BasePath -Recurse -Filter "*${Date}_${SessionId}.jsonl" | Select-Object -First 1

if (-not $file) {
    Write-Host "[ERROR] Session not found: $SessionId on $Date"
    exit 1
}

# Read all lines
$lines = Get-Content $file.FullName -Encoding UTF8

if ($Stats) {
    # Output statistics only
    $msgCount = 0
    $userCount = 0
    $assistantCount = 0
    $firstTime = ""
    $lastTime = ""
    
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try {
            $entry = $line | ConvertFrom-Json
            if ($entry.role -and $entry.time) {
                $msgCount++
                if ($entry.role -eq "user") { $userCount++ }
                if ($entry.role -eq "assistant") { $assistantCount++ }
                if (-not $firstTime) { $firstTime = $entry.time }
                $lastTime = $entry.time
            }
        } catch {}
    }
    
    Write-Host "=== Session Statistics ==="
    Write-Host "SessionId: $SessionId"
    Write-Host "Date: $Date"
    Write-Host "File: $($file.FullName)"
    Write-Host "Total Messages: $msgCount"
    Write-Host "  User: $userCount"
    Write-Host "  Assistant: $assistantCount"
    Write-Host "Time Range: $firstTime ~ $lastTime"
    Write-Host "File Size: $([math]::Round($file.Length / 1KB, 2)) KB"
    exit 0
}

# Parse all messages
$messages = @()
$lineNum = 0

foreach ($line in $lines) {
    $lineNum++
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
    try {
        $entry = $line | ConvertFrom-Json
        if ($entry.role) {
            $messages += [PSCustomObject]@{
                LineNum = $lineNum
                Time = $entry.time
                Role = $entry.role
                Text = $entry.text
                Raw = if ($Raw) { $line } else { $null }
            }
        }
    } catch {
        # Skip malformed lines
    }
}

# Output header
Write-Host "=== Session Detail: $SessionId ==="
Write-Host "File: $($file.FullName)"
Write-Host "Total Messages: $($messages.Count)"
Write-Host ""

# Filter and output
$filteredMessages = $messages

# Apply line number filter
if ($StartLine -gt 0 -and $EndLine -gt 0) {
    $filteredMessages = $filteredMessages | Where-Object { $_.LineNum -ge $StartLine -and $_.LineNum -le $EndLine }
    Write-Host "[Lines $StartLine - $EndLine]"
    Write-Host ""
}

# Apply keyword filter
if ($Keyword) {
    $matches = @()
    for ($i = 0; $i -lt $filteredMessages.Count; $i++) {
        if ($filteredMessages[$i].Text -like "*$Keyword*") {
            # Add context before
            for ($j = [Math]::Max(0, $i - $Context); $j -lt $i; $j++) {
                if ($matches -notcontains $filteredMessages[$j]) {
                    $matches += $filteredMessages[$j]
                }
            }
            # Add match itself
            if ($matches -notcontains $filteredMessages[$i]) {
                $matches += $filteredMessages[$i]
            }
            # Add context after
            for ($j = $i + 1; $j -le [Math]::Min($filteredMessages.Count - 1, $i + $Context); $j++) {
                if ($matches -notcontains $filteredMessages[$j]) {
                    $matches += $filteredMessages[$j]
                }
            }
        }
    }
    $filteredMessages = $matches | Sort-Object LineNum
    Write-Host "[Search: '$Keyword' with context ±$Context]"
    Write-Host "Found $($filteredMessages.Count) messages"
    Write-Host ""
}

# Output messages
foreach ($msg in $filteredMessages) {
    if ($Raw) {
        Write-Host $msg.Raw
    } else {
        Write-Host "[#$($msg.LineNum)] [$($msg.Time)] $($msg.Role):"
        Write-Host "$($msg.Text)"
        Write-Host ""
    }
}

Write-Host "=== End of Session ==="
