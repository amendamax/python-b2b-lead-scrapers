import os
path = r"C:\Users\bratu\.gemini\antigravity\brain\32e5e292-fe00-4763-98d4-f3fce4a17364\.system_generated\logs\transcript.jsonl"
print("Exists:", os.path.exists(path))
if os.path.exists(path):
    print("Size:", os.path.getsize(path))
