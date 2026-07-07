import os
import glob

brain_dir = r"C:\Users\bratu\.gemini\antigravity\brain"
print("Searching for non-empty transcript.jsonl files in brain...")
subdirs = [os.path.join(brain_dir, d) for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d))]

non_empty = []
for sdir in subdirs:
    tpath = os.path.join(sdir, ".system_generated", "logs", "transcript.jsonl")
    if os.path.exists(tpath) and os.path.getsize(tpath) > 0:
        non_empty.append((tpath, os.path.getsize(tpath), os.path.getmtime(tpath)))

# sort by modification time (newest first)
non_empty.sort(key=lambda x: x[2], reverse=True)

for idx, (path, size, mtime) in enumerate(non_empty[:15]):
    import datetime
    dt = datetime.datetime.fromtimestamp(mtime)
    print(f"{idx+1}. Path: {path} | Size: {size} bytes | Last Modified: {dt}")
