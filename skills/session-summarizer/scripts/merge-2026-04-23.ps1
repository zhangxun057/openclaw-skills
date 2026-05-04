$files = @(
    'C:\Users\44452\.openclaw\chat-logs\main\2026-04-23_23fdbc4b.jsonl',
    'C:\Users\44452\.openclaw\chat-logs\main\2026-04-23_29ba6b27.jsonl',
    'C:\Users\44452\.openclaw\chat-logs\main\2026-04-23_7cf628d9.jsonl'
)

$allMessages = @()
$userChars = 0
$userMsgs = 0
$aiMsgs = 0

foreach ($f in $files) {
    $lines = Get-Content $f -Encoding UTF8
    foreach ($line in $lines) {
        if ($line.Trim() -eq '') { continue }
        $msg = $line | ConvertFrom-Json
        if ($msg.role -eq 'user') {
            $userMsgs++
            $userChars += ($msg.text | Measure-Object -Character).Characters
        } elseif ($msg.role -eq 'assistant') {
            $aiMsgs++
        }
        $allMessages += $msg
    }
}

# Sort by time
$sorted = $allMessages | Sort-Object { $_.time }

@{
    totalMessages = $allMessages.Count
    userMsgs = $userMsgs
    userChars = $userChars
    userTokens = [math]::Round($userChars * 1.5)
    aiMsgs = $aiMsgs
    startTime = $sorted[0].time
    endTime = $sorted[-1].time
    sessions = 3
} | ConvertTo-Json -Depth 3
