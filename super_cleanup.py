import os
import json

DIRS = ["json_planlar", "data"]

for d in DIRS:
    index_file = os.path.join(d, "index.json")
    if not os.path.exists(index_file):
        print(f"Skipping {d}: index.json missing")
        continue
    
    with open(index_file, "r", encoding="utf-8") as f:
        idx_data = json.load(f)
    
    valid_files = {e["dosya"] for e in idx_data["dosyalar"]}
    valid_files.add("index.json")
    
    files_in_dir = [f for f in os.listdir(d) if f.endswith(".json")]
    removed = 0
    for f in files_in_dir:
        if f not in valid_files:
            os.remove(os.path.join(d, f))
            removed += 1
    print(f"Removed {removed} orphaned files from {d}.")

print("Cleanup complete.")
