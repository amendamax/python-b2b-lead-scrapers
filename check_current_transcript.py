import os
path = r"C:\Users\bratu\.gemini\antigravity\brain\e257e32a-2914-4483-bff2-848d431ded2b\.system_generated\logs\transcript.jsonl"
print("Exists:", os.path.exists(path))
if os.path.exists(path):
    print("Size:", os.path.getsize(path))
