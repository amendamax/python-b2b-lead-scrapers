import os
import glob

brain_dir = r"C:\Users\bratu\.gemini\antigravity\brain"
print("Listing conversations in brain sorted by modification time...")
subdirs = [os.path.join(brain_dir, d) for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d))]

folders_with_time = []
for sdir in subdirs:
    transcript_path = os.path.join(sdir, ".system_generated", "logs", "transcript.jsonl")
    if os.path.exists(transcript_path):
        mtime = os.path.getmtime(transcript_path)
        folders_with_time.append((sdir, mtime))
    else:
        # check the dir itself
        mtime = os.path.getmtime(sdir)
        folders_with_time.append((sdir, mtime))

folders_with_time.sort(key=lambda x: x[1], reverse=True)

for idx, (folder, mtime) in enumerate(folders_with_time[:10]):
    import datetime
    dt = datetime.datetime.fromtimestamp(mtime)
    print(f"{idx+1}. Folder: {os.path.basename(folder)} | Last Modified: {dt}")
