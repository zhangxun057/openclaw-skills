$files = @(
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_286603cf.jsonl",
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_4150058d.jsonl",
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_7cf628d9.jsonl",
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_86586be6.jsonl",
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_a86ef80e.jsonl",
    "C:\Users\44452\.openclaw\chat-logs\main\2026-04-22_ff07e815.jsonl"
)

$output = @()

foreach ($file in $files) {
    $lines = Get-Content $file
    $nonCron = @()
    foreach ($line in $lines) {
        if ($line.Trim() -eq '') { continue }
        $j = $line | ConvertFrom-Json
        if ($j.text -notmatch '\[cron:') {
            $nonCron += $line
        }
    }
    $output += @{
        filename = Split-Path $file -Leaf
        nonCronLines = $nonCron
    }
}

$output | ConvertTo-Json -Depth 5