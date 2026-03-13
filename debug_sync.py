import json
import re

def load_mapping():
    with open("official_names_mapping.json", "r", encoding="utf-8") as f:
        return json.load(f)

def fix_lesson_name(name, grade, mapping):
    if not name: return name
    new_name = name.strip()
    
    # Pre-clean
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
    
    grade_str = str(grade)
    if grade_str in mapping.get("grade_specific", {}):
        grade_map = mapping["grade_specific"][grade_str]
        upper_name = new_name.upper()
        # Debug print
        print(f"Checking {upper_name} against grade {grade_str} map keys: {list(grade_map.keys())}")
        is_official = any(val == new_name for val in grade_map.values())
        if not is_official:
            for key, official in grade_map.items():
                if key in upper_name:
                    print(f"MATCH FOUND: {key} -> {official}")
                    new_name = official
                    break

    new_name = new_name.replace("İ̇", "İ").replace("İ", "İ").replace("i̇", "i")
    new_name = re.sub(r'(-?MEB)+', '-MEB', new_name, flags=re.IGNORECASE)
    new_name = new_name.replace("(MEB)", "(MEB)").replace("-MEB", " (MEB)")
    new_name = re.sub(r'\s+', ' ', new_name).strip()
    return new_name

mapping = load_mapping()
test_name = "Beden Eğitimi"
test_grade = "1"
result = fix_lesson_name(test_name, test_grade, mapping)
print(f"Result for {test_name} (Grade {test_grade}): '{result}'")
