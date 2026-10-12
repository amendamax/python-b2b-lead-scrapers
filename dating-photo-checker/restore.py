import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's fix the static_broker_db by restoring it from the main branch
