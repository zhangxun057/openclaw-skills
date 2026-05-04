$chatlogsDir = "C:\Users\44452\.openclaw\chat-logs\main\"
$date = "2026-04-10"

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

$result = @()
foreach ($f in $files) {
    try {
        $firstLine = Get-Content $f.FullName -First 1 | ConvertFrom-Json
        $isCron = $firstLine.text -match '\[cron:'
        if (-not $isCron) {
            $result += @{
                filename = $f.Name
                path = $f.FullName
                sizeKB = [math]::Round($f.Length / 1KB, 1)
                sessionId = ($f.BaseName -replace "${date}_", "")
            }
        }
    } catch {
        $result += @{
            filename = $f.Name
            path = $f.FullName
            sizeKB = [math]::Round($f.Length / 1KB, 1)
            sessionId = ($f.BaseName -replace "${date}_", "")
        }
    }
}

$result | ConvertTo-Json -Depth 3