$chatlogsDir = "C:\Users\44452\.openclaw\chat-logs\main\"
$date = "2026-04-26"

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

# 过滤隔离会话
$filtered = @()
foreach ($f in $files) {
    try {
        $firstLine = Get-Content $f.FullName -First 1 | ConvertFrom-Json
        if ($firstLine.text -notmatch '\[cron:') {
            $filtered += @{
                filename = $f.Name
                path = $f.FullName
                sizeKB = [math]::Round($f.Length / 1KB, 1)
                sessionId = $f.BaseName -replace "${date}_", ""
            }
        }
    } catch {
        $filtered += @{
            filename = $f.Name
            path = $f.FullName
            sizeKB = [math]::Round($f.Length / 1KB, 1)
            sessionId = $f.BaseName -replace "${date}_", ""
        }
    }
}

$filtered | ConvertTo-Json -Depth 3
