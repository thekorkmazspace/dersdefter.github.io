import os
import json
import re
import unicodedata

# Paths
JSON_DIR = "json_planlar"
MAPPING_FILE = "official_names_mapping.json"
INDEX_FILE = os.path.join(JSON_DIR, "index.json")

def load_mapping():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def slugify(text):
    text = text.lower()
    text = text.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def fix_lesson_name(name, grade, mapping):
    if not name:
        return name
    
    new_name = name.strip()
    
    # 1. Exact matches (Highest priority for specific mangled names)
    if new_name in mapping["exact_matches"]:
        new_name = mapping["exact_matches"][new_name]
    
    # 2. General pattern replacements
    patterns = sorted(mapping["patterns"].items(), key=lambda x: -len(x[0]))
    for pattern, replacement in patterns:
        if pattern.isalpha():
            regex = r'\b' + re.escape(pattern) + r'\b'
            new_name = re.sub(regex, replacement, new_name, flags=re.IGNORECASE)
        else:
            new_name = new_name.replace(pattern, replacement)
            new_name = new_name.replace(pattern.lower(), replacement)

    # 3. Grade-specific overrides (For primary/middle school standards)
    grade_str = str(grade)
    if grade_str in mapping["grade_specific"]:
        grade_map = mapping["grade_specific"][grade_str]
        # Check if the current name (after basic cleaning) matches any of the keys
        upper_name = new_name.upper()
        for key, official in grade_map.items():
            if key in upper_name:
                new_name = official
                break

    # Final polish for characters
    new_name = new_name.replace("İ̇", "İ").replace("İ", "İ").replace("i̇", "i")
    
    return new_name

def get_new_filename(old_filename, new_lesson_name, grade):
    # Extract ID from original filename if possible (usually at the end before .json)
    match = re.search(r'_(\d+)\.json$', old_filename)
    id_suffix = match.group(1) if match else "000"
    
    slug = slugify(new_lesson_name)
    # Remove grade from slug if it's already there to avoid grade_1_turkce_meb_1_123.json
    slug = re.sub(rf'_{grade}$', '', slug)
    
    # Truncate slug if it's too long (Linux limit is 255 chars, but let's keep it very safe at 100)
    if len(slug) > 100:
        slug = slug[:100].strip('_')
    
    return f"grade_{grade}_{slug}_{id_suffix}.json"

def process_all(mapping):
    if not os.path.exists(INDEX_FILE):
        print("index.json not found.")
        return
        
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    updated_files_count = 0
    renamed_files_count = 0
    
    new_entries = []
    
    print(f"Starting advanced synchronization of {len(index_data['dosyalar'])} plans...")
    
    for entry in index_data["dosyalar"]:
        old_filename = entry["dosya"]
        grade = entry["sinif"]
        old_ders = entry["ders"]
        
        # 1. Fix the lesson name
        new_ders = fix_lesson_name(old_ders, grade, mapping)
        
        # 2. Determine new filename
        new_filename = get_new_filename(old_filename, new_ders, grade)
        
        # 3. Process the actual file
        old_path = os.path.join(JSON_DIR, old_filename)
        new_path = os.path.join(JSON_DIR, new_filename)
        
        if os.path.exists(old_path):
            with open(old_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            file_changed = False
            if data.get("ders") != new_ders:
                data["ders"] = new_ders
                file_changed = True
                updated_files_count += 1
            
            if file_changed or old_filename != new_filename:
                with open(old_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Rename file if name changed
            if old_filename != new_filename:
                # If target exists, maybe handle conflict or just overwrite?
                # For safety, we overwrite since we are standardizing.
                if os.path.exists(new_path) and old_path != new_path:
                    os.remove(new_path)
                os.rename(old_path, new_path)
                renamed_files_count += 1
        
        # 4. Update index entry
        entry["ders"] = new_ders
        entry["dosya"] = new_filename
        new_entries.append(entry)

    index_data["dosyalar"] = new_entries
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
        
    print(f"Summary:")
    print(f"- Updated lesson names in {updated_files_count} files.")
    print(f"- Renamed {renamed_files_count} files in the filesystem.")
    print(f"- Updated index.json with new names and filenames.")

if __name__ == "__main__":
    mapping = load_mapping()
    process_all(mapping)
