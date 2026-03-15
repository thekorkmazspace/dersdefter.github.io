import requests
import re
import json
import time

# Official Branch IDs scraped from the site
BRANŞ_IDS = [
    "1469", "543", "1242", "681", "108", "1314", "226", "232", "199", "1011", 
    "604", "1325", "272", "408", "1051", "110", "153", "200", "412", "1272", 
    "1372", "345", "1052", "1312", "1760", "303", "363", "270", "449", "1247", 
    "563", "565", "1105", "1107", "784", "1071", "1198", "606", "361", "1074", 
    "1508", "932", "1203", "973", "1073", "520", "1506", "731", "1432", "450", 
    "516", "384", "334", "1093", "283", "1075", "1062", "1056", "1332", "1072", 
    "587", "1106", "1109", "1111", "1112", "1113", "1114", "1115", "1116", "1846"
]

def scrape():
    official_map = {}
    total = len(BRANŞ_IDS)
    print(f"Starting scrape of {total} branches...")
    
    for i, bid in enumerate(BRANŞ_IDS):
        url = f"https://www.defterdoldur.com/bransgetir/{bid}/brans"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # Find plan cards: href="https://www.defterdoldur.com/plandetay/slug/ID/slug"
                # Titles are in <h3 class="ders ...">
                matches = re.finditer(r'href=".*?/plandetay/.*?/(\d+)/.*?".*?>(.*?)</a>', resp.text, re.DOTALL)
                count = 0
                for m in matches:
                    pid = m.group(1)
                    block_content = m.group(2)
                    
                    # Target the h3 with class ders
                    h3_match = re.search(r'<h3[^>]*class="[^"]*ders[^"]*"[^>]*>(.*?)</h3>', block_content, re.DOTALL)
                    if h3_match:
                        title = re.sub(r'<.*?>', '', h3_match.group(1)).strip()
                    else:
                        title = re.sub(r'<.*?>', '', block_content).strip()
                    
                    # Clean up multiple spaces and newlines
                    title = re.sub(r'\s+', ' ', title)
                    
                    if title and pid not in official_map:
                        official_map[pid] = title
                        count += 1
                
                print(f" [{i+1}/{total}] Branch {bid}: Found {count} plans")
            else:
                print(f" [{i+1}/{total}] Branch {bid}: Error {resp.status_code}")
        except Exception as e:
            print(f" [{i+1}/{total}] Branch {bid}: Exception {e}")
        
        time.sleep(0.3)

    return official_map

if __name__ == "__main__":
    results = scrape()
    with open("data/official_names.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nScrape complete. Total unique plans: {len(results)}")
