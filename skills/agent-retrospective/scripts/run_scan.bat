# Run health scan and save output
python "C:\Users\44452\.openclaw\skills\agent-retrospective\scripts\health_scan.py" --days 2 --date 2026-04-20 > "C:\Users\44452\.openclaw\skills\agent-retrospective\scripts\scan_result.json"
# Run write evolution
python "C:\Users\44452\.openclaw\skills\agent-retrospective\scripts\write_evolution.py" --date 2026-04-20 --input "C:\Users\44452\.openclaw\skills\agent-retrospective\scripts\scan_result.json"