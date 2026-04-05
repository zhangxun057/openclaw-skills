# segment-messages.ps1
# 将大型 ChatLogs 文件分段，每段固定消息数

param(
    [string]$inputPath,
    [int]$segmentSize = 200,
    [string]$outputDir
)

# 读取 JSONL 文件
$lines = Get-Content -Path $inputPath | Where-Object { $_.Trim() }

# 计算分段数
$totalLines = $lines.Count
$segmentCount = [math]::Ceiling($totalLines / $segmentSize)

# 确保输出目录存在
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# 分段写入
$segments = @()
for ($i = 0; $i -lt $segmentCount; $i++) {
    $startIndex = $i * $segmentSize
    $endIndex = [math]::Min(($startIndex + $segmentSize), $totalLines)
    $segmentLines = $lines[$startIndex..($endIndex - 1)]
    
    $segmentFilename = "segment_$i.jsonl"
    $segmentPath = Join-Path $outputDir $segmentFilename
    $segmentLines | Set-Content -Path $segmentPath
    
    $segments += @{
        segmentIndex = $i
        filename = $segmentFilename
        path = $segmentPath
        messageCount = $segmentLines.Count
    }
}

@{
    totalSegments = $segmentCount
    totalMessages = $totalLines
    segments = $segments
} | ConvertTo-Json -Depth 3
