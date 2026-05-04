$merged = @()
$files = @(
    @{path='C:\Users\44452\.openclaw\chat-logs\main\2026-04-20_13fdbd9a.jsonl'; sizeKB=17.1; sessionId='13fdbd9a'; isCron=$false},
    @{path='C:\Users\44452\.openclaw\chat-logs\main\2026-04-20_7cf628d9.jsonl'; sizeKB=0.2; sessionId='7cf628d9'; isCron=$false},
    @{path='C:\Users\44452\.openclaw\chat-logs\main\2026-04-20_8cf9edc5.jsonl'; sizeKB=54; sessionId='8cf9edc5'; isCron=$false},
    @{path='C:\Users\44452\.openclaw\chat-logs\main\2026-04-20_8fb751b6.jsonl'; sizeKB=0.6; sessionId='8fb751b6'; isCron=$false}
)

$userMsgs = 0
$userChars = 0
$aiMsgs = 0
$allMessages = @()
$startTime = $null
$endTime = $null

foreach ($f in $files) {
    if ($f.isCron) { continue }
    $lines = Get-Content $f.path -Encoding utf8
    foreach ($line in $lines) {
        if ($line.Trim() -eq '') { continue }
        try {
            $msg = $line | ConvertFrom-Json
            $allMessages += $msg
            if ($msg.role -eq 'user') {
                $userMsgs++
                $userChars += ($msg.text | Measure-Object -Character).Characters
            } elseif ($msg.role -eq 'assistant') {
                $aiMsgs++
            }
            if (-not $startTime -or $msg.time -lt $startTime) { $startTime = $msg.time }
            if (-not $endTime -or $msg.time -gt $endTime) { $endTime = $msg.time }
        } catch {}
    }
}

$allMessages = $allMessages | Sort-Object { $_.time }

@{
    totalSessions = ($files | Where-Object { -not $_.isCron }).Count
    totalSizeKB = ($files | Where-Object { -not $_.isCron } | Measure-Object -Property sizeKB -Sum).Sum
    userMsgs = $userMsgs
    userChars = $userChars
    userTokens = [math]::Round($userChars * 1.5)
    aiMsgs = $aiMsgs
    totalMsgs = $allMessages.Count
    startTime = $startTime
    endTime = $endTime
    firstThree = $allMessages[0..2] | ForEach-Object { "$($_.time) [$($_.role)]: $($_.text.Substring(0, [math]::Min(100, $_.text.Length)))" }
    lastThree = $allMessages[-3..-1] | ForEach-Object { "$($_.time) [$($_.role)]: $($_.text.Substring(0, [math]::Min(100, $_.text.Length)))" }
} | ConvertTo-Json -Depth 5