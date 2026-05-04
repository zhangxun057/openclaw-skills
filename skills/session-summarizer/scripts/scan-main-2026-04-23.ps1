$chatlogsDir = 'C:\Users\44452\.openclaw\chat-logs\main'
$date = '2026-04-23'
$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 0 }
$files | ForEach-Object {
    $firstLine = $null
    try { $firstLine = Get-Content $_.FullName -First 1 | ConvertFrom-Json } catch {}
    $shouldExclude = $firstLine -and ($firstLine.text -match '\[cron:')
    if (-not $shouldExclude) {
        [PSCustomObject]@{
            filename = $_.Name
            path = $_.FullName
            sizeKB = [math]::Round($_.Length / 1KB, 1)
            sessionId = ($_.BaseName -replace "${date}_", "")
        }
    }
} | ConvertTo-Json -Depth 3
