param(
    [string]$chatlogsDir,
    [string]$date
)

if (!(Test-Path $chatlogsDir)) {
    Write-Output '[]'
    exit
}

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

# 过滤隔离会话
$files = $files | Where-Object {
    try {
        $firstLine = Get-Content $_.FullName -First 1 | ConvertFrom-Json
        return $firstLine.text -notmatch '\[cron:'
    } catch {
        return $true
    }
}

$result = $files | ForEach-Object {
    @{
        filename = $_.Name
        path = $_.FullName
        sizeKB = [math]::Round($_.Length / 1KB, 1)
        sessionId = ($_.BaseName -replace "${date}_", "")
    }
}

$result | ConvertTo-Json -Depth 3