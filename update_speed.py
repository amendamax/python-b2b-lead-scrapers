import re

def append_to_solution(filepath, original_text, new_text):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if original_text in content:
        content = content.replace(original_text, new_text)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Text not found in {filepath}")

# EN
en_orig = "evading quota limits (Status 429)."
en_new = "evading quota limits (Status 429), ensuring all newly generated pages are fully indexed and discoverable in Google Search in under 2 hours."
append_to_solution("index.html", en_orig, en_new)

# RO
ro_orig = "ocolind blocajele de cotă zilnică."
ro_new = "ocolind blocajele de cotă zilnică. Toate paginile noi sunt implementate și gata să fie regăsite în Google Search instant, în maximum 2 ore de la generare."
append_to_solution("ro/index.html", ro_orig, ro_new)

# IT
it_orig = "eludendo i blocchi (Status 429)."
it_new = "eludendo i blocchi (Status 429), garantendo che tutte le nuove pagine generate siano completamente indicizzate e reperibili istantaneamente su Google Search in meno di 2 ore."
append_to_solution("it/index.html", it_orig, it_new)

