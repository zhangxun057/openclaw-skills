# scan-files.ps1
# 扫描指定日期的 ChatLogs 文件，返回文件列表和大小信息

param(
    [string]$chatlogsDir,
    [string]$date
)

$pattern = "${date}_*.jsonl"
$files = Get-ChildItem -Path $chatlogsDir -Filter $pattern -ErrorAction SilentlyContinue

$result = $files | ForEach-Object {
    @{
        filename = $_.Name
        path = $_.FullName
        sizeKB = [math]::Round($_.Length / 1KB, 1)
        sessionId = ($_.BaseName -replace "${date}_", "")
    }
}

$result | ConvertTo-Json -Depth 3
