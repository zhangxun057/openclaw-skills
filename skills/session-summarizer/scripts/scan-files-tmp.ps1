$chatlogsDir = "C:\Users\44452\.openclaw\chat-logs\main"
$date = "2026-04-22"

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

$result = $files | ForEach-Object {
    @{
        filename = $_.Name
        sizeKB = [math]::Round($_.Length / 1KB, 1)
        sessionId = $_.BaseName.Replace("${date}_", "")
    }
}

$result | ConvertTo-Json -Depth 3