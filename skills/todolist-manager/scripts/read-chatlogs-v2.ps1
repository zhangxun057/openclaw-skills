# read-chatlogs-v2.ps1
# Function: Read chat-logs with batch/single/digest modes
# Usage: 
#   Batch mode:   powershell -File "read-chatlogs-v2.ps1" -Date "2026-03-23" -Mode batch
#   Single mode:  powershell -File "read-chatlogs-v2.ps1" -Date "2026-03-23" -SessionId "abc123" [-Context 10]
#   Digest mode:  powershell -File "read-chatlogs-v2.ps1" -Date "2026-03-23" -Mode digest -SkillType "todo"|"diary"

param(
    [string]$Date = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd"),
    [string]$Mode = "batch",     # batch | single | digest
    [string]$SessionId = "",      # required for single/digest mode
    [int]$Context = 0,            # for single mode: include N messages around keyword
    [string]$Keyword = "",        # for single mode: search keyword
    [string]$SkillType = "",      # for digest mode: "todo" or "diary"
    [string]$OutputPath = ""      # for digest mode: optional custom output path
)

$BasePath = "C:\Users\44452\.openclaw\chat-logs"
$Agents = @("guaiguaixia", "lelexia", "main", "pipipixia", "zhuizhuixia")

function Get-SessionList {
    param([string]$TargetDate)
    
    $sessions = @()
    foreach ($agent in $Agents) {
        $agentPath = Join-Path $BasePath $agent
        if (Test-Path $agentPath) {
            $files = Get-ChildItem $agentPath -Filter "*.jsonl" -ErrorAction SilentlyContinue | 
                     Where-Object { $_.Name -like "*${TargetDate}*" }
            
            foreach ($file in $files) {
                $sid = $file.Name -replace "^${TargetDate}_", "" -replace "\.jsonl$", ""
                $sessions += [PSCustomObject]@{
                    SessionId = $sid
                    Agent = $agent
                    SizeKB = [math]::Round($file.Length / 1KB, 2)
                    Path = $file.FullName
                    MessageCount = (Get-Content $file.FullName | Measure-Object).Count
                }
            }
        }
    }
    return $sessions | Sort-Object SizeKB -Descending
}

function Read-SessionContent {
    param(
        [string]$FilePath,
        [int]$Context = 0,
        [string]$Keyword = ""
    )
    
    $lines = Get-Content $FilePath -Encoding UTF8
    $messages = @()
    $lineNum = 0
    
    foreach ($line in $lines) {
        $lineNum++
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        
        try {
            $entry = $line | ConvertFrom-Json
            if ($entry.role -and $entry.text) {
                $messages += [PSCustomObject]@{
                    LineNum = $lineNum
                    Time = $entry.time
                    Role = $entry.role
                    Text = $entry.text
                }
            }
        } catch {
            # Skip malformed lines
        }
    }
    
    # If keyword search requested
    if ($Keyword -and $messages.Count -gt 0) {
        $matches = @()
        for ($i = 0; $i -lt $messages.Count; $i++) {
            if ($messages[$i].Text -like "*$Keyword*") {
                $start = [Math]::Max(0, $i - $Context)
                $end = [Math]::Min($messages.Count - 1, $i + $Context)
                for ($j = $start; $j -le $end; $j++) {
                    if ($matches -notcontains $messages[$j]) {
                        $matches += $messages[$j]
                    }
                }
            }
        }
        return $matches | Sort-Object LineNum
    }
    
    return $messages
}

function Get-SessionDigestTemplate {
    param([string]$Type)
    
    if ($Type -eq "todo") {
        return @"
### Session: {SessionId} ({Agent}) · {SizeKB}KB

**时间范围**：{TimeRange}  
**消息数**：{MessageCount}

#### 任务视角
- **完成的任务**：
- **断线头/待跟进**：
- **新增待办**：

#### 关键对话
- 行号范围：#X - #Y
- 精读提示：搜索"关键词"

---
"@
    }
    elseif ($Type -eq "diary") {
        return @"
### Session: {SessionId} ({Agent}) · {SizeKB}KB

**时间范围**：{TimeRange}  
**消息数**：{MessageCount}

#### 日记视角
- **选题方向**：
- **技术洞察**：
- **决策记录**：
- **方法论**：

#### 关键对话
- 行号范围：#X - #Y
- 精读提示：搜索"关键词"

---
"@
    }
    else {
        return @"
### Session: {SessionId} ({Agent}) · {SizeKB}KB

**时间范围**：{TimeRange}  
**消息数**：{MessageCount}

#### 内容摘要
[待填写]

#### 关键对话
- 行号范围：#X - #Y
- 精读提示：搜索"关键词"

---
"@
    }
}

# Main logic
if ($Mode -eq "batch") {
    # Batch mode: return session list
    Write-Host "=== Session List for $Date ==="
    Write-Host ""
    
    $sessions = Get-SessionList -TargetDate $Date
    
    if ($sessions.Count -eq 0) {
        Write-Host "[WARN] No sessions found for $Date"
        exit 1
    }
    
    $sessions | ForEach-Object {
        Write-Host "Session: $($_.SessionId)"
        Write-Host "  Agent: $($_.Agent)"
        Write-Host "  Size: $($_.SizeKB) KB"
        Write-Host "  Messages: $($_.MessageCount)"
        Write-Host "  Path: $($_.Path)"
        Write-Host ""
    }
    
    Write-Host "=== Total: $($sessions.Count) sessions ==="
} 
elseif ($Mode -eq "single") {
    # Single mode: return session content
    if (-not $SessionId) {
        Write-Host "[ERROR] SessionId required for single mode"
        exit 1
    }
    
    $file = Get-ChildItem -Path $BasePath -Recurse -Filter "*${Date}_${SessionId}.jsonl" | Select-Object -First 1
    
    if (-not $file) {
        Write-Host "[ERROR] Session not found: $SessionId on $Date"
        exit 1
    }
    
    Write-Host "=== Session: $SessionId ==="
    Write-Host "File: $($file.FullName)"
    Write-Host ""
    
    $messages = Read-SessionContent -FilePath $file.FullName -Context $Context -Keyword $Keyword
    
    if ($Keyword) {
        Write-Host "[Search: '$Keyword' with context $Context]"
        Write-Host "Found $($messages.Count) messages"
        Write-Host ""
    }
    
    foreach ($msg in $messages) {
        Write-Host "[#$($msg.LineNum)] [$($msg.Time)] $($msg.Role):"
        Write-Host "$($msg.Text)"
        Write-Host ""
    }
    
    Write-Host "=== End of Session ==="
}
elseif ($Mode -eq "digest") {
    # Digest mode: generate digest template
    if (-not $SkillType) {
        Write-Host "[ERROR] SkillType required for digest mode (todo|diary)"
        exit 1
    }
    
    # Determine output path
    if (-not $OutputPath) {
        $OutputPath = "C:\Users\44452\.openclaw\agents\main\workspace\scratchpad\digest\${SkillType}-${Date}.md"
    }
    
    # Ensure directory exists
    $OutputDir = Split-Path $OutputPath -Parent
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    # Get all sessions
    $sessions = Get-SessionList -TargetDate $Date
    
    if ($sessions.Count -eq 0) {
        Write-Host "[WARN] No sessions found for $Date"
        exit 1
    }
    
    # Generate digest header
    $header = @"
# Session Digest · ${Date}

## 当日概览

| 指标 | 数值 |
|------|------|
| 总 Session 数 | $($sessions.Count) |
| 最大 Session | $($sessions[0].Agent) ($($sessions[0].SizeKB) KB, $($sessions[0].MessageCount) 条) |

---

"@

    # Generate session templates
    $body = ""
    foreach ($session in $sessions) {
        # Get first and last message times
        $content = Read-SessionContent -FilePath $session.Path
        $firstTime = if ($content.Count -gt 0) { $content[0].Time } else { "未知" }
        $lastTime = if ($content.Count -gt 0) { $content[$content.Count - 1].Time } else { "未知" }
        $timeRange = "$firstTime ~ $lastTime"
        
        $template = Get-SessionDigestTemplate -Type $SkillType
        $template = $template -replace "{SessionId}", $session.SessionId
        $template = $template -replace "{Agent}", $session.Agent
        $template = $template -replace "{SizeKB}", $session.SizeKB
        $template = $template -replace "{MessageCount}", $session.MessageCount
        $template = $template -replace "{TimeRange}", $timeRange
        
        $body += $template + "`n"
    }
    
    # Write digest file
    $fullContent = $header + $body
    $fullContent | Out-File -FilePath $OutputPath -Encoding UTF8
    
    Write-Host "=== Digest Generated ==="
    Write-Host "Path: $OutputPath"
    Write-Host "Sessions: $($sessions.Count)"
    Write-Host "Skill Type: $SkillType"
}
else {
    Write-Host "[ERROR] Invalid mode. Use 'batch', 'single', or 'digest'"
    exit 1
}
