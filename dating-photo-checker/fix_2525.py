import re

with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will replace all instances of }}}; with }};
content = content.replace("}}});", "}});")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(content)
