import json
from pathlib import Path

chatlogs_dir = Path(r"C:\Users\44452\.openclaw\chat-logs\main")
date = "2026-04-22"

files = list(chatlogs_dir.glob(f"{date}_*.jsonl"))
print(f"Found {len(files)} session files")

all_messages = []
user_stats = {"msgs": 0, "chars": 0, "aiMsgs": 0}

for f in files:
    try:
        content = f.read_text(encoding="utf-8")
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                if obj.get("role") == "user":
                    text = obj.get("text", "")
                    if text.startswith("[cron:"):
                        continue
                    user_stats["msgs"] += 1
                    user_stats["chars"] += len(text)
                    all_messages.append(obj)
                elif obj.get("role") == "assistant":
                    user_stats["aiMsgs"] += 1
                    all_messages.append(obj)
            except:
                pass
    except Exception as e:
        print(f"Error reading {f}: {e}")

print(f"Total messages: {len(all_messages)}")
print(f"User msgs: {user_stats['msgs']}, chars: {user_stats['chars']}, aiMsgs: {user_stats['aiMsgs']}")

if all_messages:
    times = [m.get("time", "") for m in all_messages if m.get("time")]
    if times:
        print(f"Time range: {min(times)[11:16]} ~ {max(times)[11:16]}")

# Print all messages (role + first 150 chars)
print("\n=== ALL MESSAGES (first 150 chars) ===")
for m in all_messages:
    role = m.get("role", "?")
    time_str = m.get("time", "")[11:16]
    text = m.get("text", "")
    # Encode to ascii, replace errors
    safe_text = text[:150].encode('ascii', 'replace').decode('ascii')
    print(f"[{time_str}][{role}] {safe_text}")
    print("---")