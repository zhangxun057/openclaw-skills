# 每日拜访访谈提醒脚本
$stateFile = "$env:USERPROFILE\.openclaw\workspace\skills\interview-tracker\state.json"
$currentTime = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()

# 激活访谈状态
$state = @{
    active = $true
    round = 1
    start_time = $currentTime
    data = @{
        "拜访者" = "张洵"
        "客户名称" = ""
        "客户类型" = ""
        "与客户关系" = ""
        "拜访日期" = $currentTime
        "联系人姓名" = ""
        "联系人职务" = ""
        "联系方式" = ""
        "拜访目的" = @()
        "沟通内容摘要" = ""
        "客户需求" = ""
        "客户背景信息" = ""
        "意向程度" = ""
        "下次跟进时间" = $null
        "备注" = ""
    }
}

$state | ConvertTo-Json -Depth 10 | Set-Content -Path $stateFile -Encoding UTF8

# 通过 openclaw 发送飞书消息
& openclaw message send --channel feishu --to "user:ou_fa304d207540db7ee7356a1ef4d5285c" --message "张总好！该记录今天的客户拜访信息了。`n`n**第1轮访谈：**`n今天拜访了哪个客户？您和客户是什么关系？"

Write-Host "✅ 访谈提醒已发送"
