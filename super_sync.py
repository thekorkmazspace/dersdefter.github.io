import os
import json
import re
import shutil

# Paths
MAPPING_FILE = "official_names_mapping.json"
CURRICULUM_FILE = "curriculum.json"
DIRS_TO_SYNC = ["json_planlar", "data"]

def load_mapping():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def slugify(text):
    text = text.lower()
    text = text.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

import unicodedata

def tr_upper(text):
    if not text: return ""
    return text.replace("i", "İ").replace("ı", "I").upper()

def fix_lesson_name(name, grade, mapping):
    if not name: return name
    # Normalize to NFC to avoid decomposed characters (like i + dot)
    name = unicodedata.normalize('NFC', name)
    new_name = name.strip()
    
    # Pre-clean: Remove common redundant repetitions caused by previous runs
    new_name = re.sub(r'(-?MEB)+', '-MEB', new_name, flags=re.IGNORECASE)
    new_name = re.sub(r'(Yeni\*)+', 'Yeni*', new_name, flags=re.IGNORECASE)
    
    if new_name in mapping["exact_matches"]:
        new_name = mapping["exact_matches"][new_name]
    
    patterns = sorted(mapping["patterns"].items(), key=lambda x: -len(x[0]))
    for pattern, replacement in patterns:
        if replacement in new_name:
            continue
        if pattern.isalpha():
            regex = r'\b' + re.escape(pattern) + r'\b'
            new_name = re.sub(regex, replacement, new_name, flags=re.IGNORECASE)
        else:
            new_name = new_name.replace(pattern, replacement)
            new_name = new_name.replace(pattern.lower(), replacement)
    
    # Grade-specific overrides
    grade_str = str(grade)
    if grade_str in mapping.get("grade_specific", {}):
        grade_map = mapping["grade_specific"][grade_str]
        upper_name = tr_upper(new_name)
        # Only apply grade specific if the name isn't already official
        is_official = any(val == new_name for val in grade_map.values())
        if not is_official:
            for key, official in grade_map.items():
                if tr_upper(key) in upper_name:
                    new_name = official
                    break

    new_name = new_name.replace("İ̇", "İ").replace("İ", "İ").replace("i̇", "i")
    # Final cleanup of any double MEB or Yeni* resulting from grade_specific
    new_name = re.sub(r'\(?\s?\(?MEB\)?\s?\)?', ' (MEB)', new_name, flags=re.IGNORECASE)
    new_name = re.sub(r'(Yeni\*)+', 'Yeni*', new_name, flags=re.IGNORECASE)
    
    # Ensure MEB doesn't have double parens
    new_name = new_name.replace("((MEB))", "(MEB)").replace("( (MEB))", "(MEB)")
    
    # If grade specific already added -X, ensure we don't double it
    new_name = re.sub(r'-(\d+)-(\d+)', r'-\1', new_name)
    
    new_name = re.sub(r'\s+', ' ', new_name).strip()
    return new_name

def get_new_filename(old_filename, new_lesson_name, grade):
    match = re.search(r'_(\d+)\.json$', old_filename)
    id_suffix = match.group(1) if match else "000"
    slug = slugify(new_lesson_name)
    slug = re.sub(rf'_{grade}$', '', slug)
    if len(slug) > 100: slug = slug[:100].strip('_')
    return f"grade_{grade}_{slug}_{id_suffix}.json"

def process_directory(dir_name, mapping):
    index_file = os.path.join(dir_name, "index.json")
    if not os.path.exists(index_file):
        print(f"Index not found in {dir_name}")
        return
        
    with open(index_file, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    new_entries = []
    print(f"Processing directory: {dir_name}")
    
    for entry in index_data["dosyalar"]:
        old_filename = entry["dosya"]
        grade = entry["sinif"]
        old_ders = entry["ders"]
        
        new_ders = fix_lesson_name(old_ders, grade, mapping)
        new_filename = get_new_filename(old_filename, new_ders, grade)
        
        old_path = os.path.join(dir_name, old_filename)
        new_path = os.path.join(dir_name, new_filename)
        
        # In 'data' folder, we might be missing the file. 
        # We should try to find it in 'json_planlar' if missing.
        source_path = old_path
        if not os.path.exists(old_path) and dir_name == "data":
            # Try to find in json_planlar
            staging_path = os.path.join("json_planlar", old_filename)
            if os.path.exists(staging_path):
                source_path = staging_path
            else:
                # Last resort: try to find by ID
                match = re.search(r'_(\d+)\.json$', old_filename)
                if match:
                    id_val = match.group(1)
                    for sjf in os.listdir("json_planlar"):
                        if sjf.endswith(f"_{id_val}.json"):
                            source_path = os.path.join("json_planlar", sjf)
                            break

        if os.path.exists(source_path):
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data["ders"] = new_ders
                data["sinif"] = str(grade)
            
            # Save to temporary then move
            temp_path = new_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(new_path) and new_path != temp_path:
                os.remove(new_path)
            os.rename(temp_path, new_path)
            
            # Remove old file if name changed and it's not the new one
            if old_path != new_path and os.path.exists(old_path):
                os.remove(old_path)
        
        entry["ders"] = new_ders
        entry["dosya"] = new_filename
        new_entries.append(entry)

    index_data["dosyalar"] = new_entries
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def update_curriculum(mapping):
    if not os.path.exists(CURRICULUM_FILE): return
    print("Updating curriculum.json...")
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "grades" in data:
        for grade, lessons in data["grades"].items():
            for lesson in lessons:
                old_name = lesson.get("subject_name", "")
                new_name = fix_lesson_name(old_name, grade, mapping)
                lesson["subject_name"] = new_name
                if "outcomes" in lesson:
                    for outcome in lesson["outcomes"]:
                        outcome["subject_name"] = new_name
                        
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mapping = load_mapping()
    # 1. First process json_planlar to have all files standardized
    process_directory("json_planlar", mapping)
    # 2. Then process data (which will pull from json_planlar if files are missing)
    process_directory("data", mapping)
    # 3. Finally update curriculum.json
    update_curriculum(mapping)
    print("Super sync complete.")
