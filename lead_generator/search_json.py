import re

def search_json():
    print("Searching for data patterns in pg_sample.html...")
    with open("pg_sample.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    # Search for common JSON data script tags
    patterns = [
        r'__NEXT_DATA__',
        r'window\.__PRELOADED_STATE__',
        r'window\._IOL_STATE_',
        r'type="application/json"',
        r'var feOptions',
        r'var iolData',
        r'data-state'
    ]
    
    for p in patterns:
        matches = list(re.finditer(p, html))
        print(f"Pattern '{p}': found {len(matches)} matches")
        if matches:
            idx = matches[0].start()
            print("Snippet around first match:")
            print(html[max(0, idx-100):min(len(html), idx+300)])
            print("-" * 50)
            
if __name__ == "__main__":
    search_json()
