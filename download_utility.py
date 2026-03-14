import requests
import os

ids = [1949, 1428, 1539, 1622, 1697, 1669, 1953]
os.makedirs("word_planlar", exist_ok=True)

for i in ids:
    url = f"https://defterdoldur.com/planword/{i}"
    print(f"Downloading {i}...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(f"word_planlar/downloaded_{i}.docx", "wb") as f:
                f.write(r.content)
            print(f"Saved {i}")
        else:
            print(f"Failed {i}: {r.status_code}")
    except Exception as e:
        print(f"Error {i}: {e}")
