import json
import sys

transcript_path = r"C:\Users\bratu\.gemini\antigravity\brain\8960e2a1-35c4-4c3d-b5da-5f0490b1f189\.system_generated\logs\transcript.jsonl"
inputs = []
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'USER_INPUT':
                inputs.append(data.get('content', ''))
        except:
            pass

for i in inputs[-30:]:
    print(i)
    print("-----")
