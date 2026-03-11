import os
import json
import re

# Paths
JSON_DIR = "json_planlar"
MAPPING_FILE = "official_names_mapping.json"
INDEX_FILE = os.path.join(JSON_DIR, "index.json")

def load_mapping():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def fix_lesson_name(name, mapping):
    if not name:
        return name
    
    # Clean up common debris first
    new_name = name.strip()
    
    # 1. Exact matches first
    if new_name in mapping["exact_matches"]:
        return mapping["exact_matches"][new_name]
    
    # 2. Pattern replacements
    # Sort patterns by length descending to avoid partial matches on long words
    patterns = sorted(mapping["patterns"].items(), key=lambda x: -len(x[0]))
    
    for pattern, replacement in patterns:
        # Use word boundaries if it's a word-like pattern
        if pattern.isalpha():
            regex = r'\b' + re.escape(pattern) + r'\b'
            new_name = re.sub(regex, replacement, new_name, flags=re.IGNORECASE)
        else:
            # For non-alpha (like YEN*), simple replace
            new_name = new_name.replace(pattern, replacement)
            new_name = new_name.replace(pattern.lower(), replacement)

    # Final polish for characters
    new_name = new_name.replace("İ̇", "İ").replace("İ", "İ").replace("i̇", "i")
    
    # Proper casing (Title case but respect Turkish rules)
    # Actually, most names are in Title Case or ALL CAPS in Defterdoldur.
    # I'll stick to a clean version of what's intended.
    
    return new_name

def process_plan_files(mapping):
    files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json") and f != "index.json"]
    print(f"Processing {len(files)} plan files...")
    
    count = 0
    for file_name in files:
        file_path = os.path.join(JSON_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        old_name = data.get("ders", "")
        new_name = fix_lesson_name(old_name, mapping)
        
        if old_name != new_name:
            data["ders"] = new_name
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            count += 1
            
    print(f"Updated {count} plan files.")

def update_index_json(mapping):
    if not os.path.exists(INDEX_FILE):
        print("index.json not found.")
        return
        
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
        
    count = 0
    for entry in index_data.get("dosyalar", []):
        old_name = entry.get("ders", "")
        new_name = fix_lesson_name(old_name, mapping)
        if old_name != new_name:
            entry["ders"] = new_name
            count += 1
            
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
        
    print(f"Updated {count} entries in index.json.")

if __name__ == "__main__":
    mapping = load_mapping()
    process_plan_files(mapping)
    update_index_json(mapping)
