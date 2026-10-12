import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will find all instances of single braces inside the geo-meta fetch block
# Actually, let's just find "if (propCard) {" and replace it globally.
# There are several inside this block.
content = content.replace("if (propCard) {", "if (propCard) {{")
content = content.replace("if (props.length > 0) {", "if (props.length > 0) {{")
content = content.replace("if (badge) { ", "if (badge) {{ ")
content = content.replace("badge.style.background = \"rgba(14, 165, 233, 0.2)\"; ", "badge.style.background = \"rgba(14, 165, 233, 0.2)\"; ")
content = content.replace("badge.style.color = \"#38bdf8\"; ", "badge.style.color = \"#38bdf8\"; ")
content = content.replace("}\n                    \n                    const p1", "}}\n                    \n                    const p1")
content = content.replace("}\n            }\n        }}\n    }}).catch", "}}\n            }}\n        }}\n    }}).catch")
content = content.replace("}\n            }\n        }\n    }).catch", "}}\n            }}\n        }}\n    }}).catch")
content = content.replace("badge.style.background = \"rgba(56, 189, 248, 0.1)\"; \n                        badge.style.color = \"#38bdf8\"; \n                    }", "badge.style.background = \"rgba(56, 189, 248, 0.1)\"; \n                        badge.style.color = \"#38bdf8\"; \n                    }}")

with open("dating-photo-checker/server.py", "w", encoding="utf-8") as f:
    f.write(content)
