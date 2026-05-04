$outDir = 'C:\Users\44452\.openclaw\chat-logs\summaries'
if (-not (Test-Path -Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
Write-Output "OK"