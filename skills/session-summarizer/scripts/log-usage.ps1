$logDir = 'C:\Users\44452\.openclaw\skill-logs\session-summarizer'
if (-not (Test-Path -Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$logFile = Join-Path $logDir 'log.md'
$entry = "## [2026-04-25 14:24:00]`n- **日期**: 2026-04-24`n- **Agent**: main`n- **会话数**: 2`n- **处理模式**: direct（小文件，14.9KB）`n- **结果**: 成功`n"
Add-Content -Path $logFile -Value $entry -Encoding utf8