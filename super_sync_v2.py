#!/usr/bin/env python3
import os, json, re, shutil

# Base path
BASE_DIR = "/home/fatih/Masaüstü/Yıllık Planlar"
SOURCE_DIR = os.path.join(BASE_DIR, "json_planlar")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_JP_DIR = os.path.join(BASE_DIR, "data/json_planlar")

# Load official names if available
OFFICIAL_NAMES = {}
OFF_PATH = os.path.join(DATA_DIR, "official_names.json")
if os.path.exists(OFF_PATH):
    try:
        with open(OFF_PATH, "r", encoding="utf-8") as f:
            OFFICIAL_NAMES = json.load(f)
    except: pass

import unicodedata

RESTORATION_MAP = {
    "ETKNLK": "ETKİNLİK", "ETKNLKLER": "ETKİNLİKLER",
    "SNF": "SINIF", "MAARF": "MAARİF",
    "MATEMATK": "MATEMATİK", "BLM": "BİLİM",
    "DN": "DİN", "TURKCE": "TÜRKÇE", "TRKCE": "TÜRKÇE",
    "GORSEL": "GÖRSEL", "SANATLARE": "SANATLAR",
    "ELEKTRK": "ELEKTRİK", "ELEKTRONK": "ELEKTRONİK", "ELEKTROṄK": "ELEKTRONİK",
    "TEKNOLOJS": "TEKNOLOJİSİ", "TEKNOLOJLER": "TEKNOLOJİLER",
    "İNGİLİZCE": "İNGİLİZCE", "CHAZ": "CİHAZ", "SISTEM": "SİSTEM",
    "TRK DL EDEBYATI": "TÜRK DİLİ VE EDEBİYATI",
    "EDEBYATI": "EDEBİYATI", "EDEBYAT": "EDEBİYAT",
    "BEDEN EGT": "BEDEN EĞİTİMİ", "FZK": "FİZİK",
    "BLGSAYAR": "BİLGİSAYAR", "MZK": "MÜZİK",
    "TESSAT": "TESİSAT", "GYM": "GİYİM", "MAKNELER": "MAKİNELER",
    "MMAR": "MİMARİ", "TRNE": "TÜRÜNE", "LABORATUVAR": "LABORATUVAR",
    "ANATOM": "ANATOMİ", "FZYOLOJ": "FİZYOLOJİ", "ADL": "ADLİ",
    "MCADELE": "MÜCADELE", "ARCLK": "ARICILIK", "GYSI": "GİYSİ", "ÜRETIM": "ÜRETİMİ"
}

def fix_lesson_name(name, grade, file_id):
    # 0. Unicode Normalization (NFKD) to strip combining marks (like dots over letters)
    name = unicodedata.normalize('NFKD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    
    # Fix common I conversion issue after normalization
    name = name.replace("ı̇", "i").replace("İ", "İ").replace("i̇", "i")
    
    # 1. Use absolute truth from site if ID found
    if str(file_id) in OFFICIAL_NAMES:
        return OFFICIAL_NAMES[str(file_id)]
    
    # 2. General restoration
    name = name.upper()
    for bad, good in RESTORATION_MAP.items():
        name = re.sub(r'\b' + re.escape(bad) + r'\b', good, name)
    
    # 3. Strip noise
    name = re.sub(r'\(YEN.*\)', '', name)
    name = re.sub(r'\(MEB.*\)', '', name)
    name = re.sub(r'\(MESEM.*\)', '', name, flags=re.IGNORECASE)
    name = name.replace("UYGULAMA(YEN*)", "UYGULAMALARI").replace("UYGULAMAYEN", "UYGULAMALARI")
    
    # Final check for common mistakes
    if "TÜRK DİLİ EDEBİYATI" in name:
        name = name.replace("TÜRK DİLİ EDEBİYATI", "TÜRK DİLİ VE EDEBİYATI")
    
    # Clean up excess spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    if len(name) > 80: name = name[:77] + "..."
    return name

def slugify(name):
    name = name[:50]
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    name = name.translate(tr_map).lower()
    name = re.sub(r'[^a-z0-9_]', '', name)
    return re.sub(r'_+', '_', name).strip('_')

def run_sync():
    print("Starting Super Sync V3 (Directory Scan Mode)...")
    
    new_idx_list = []
    # Scan all files in the directory instead of index.json
    all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".json") and f != "index.json"]
    
    for old_file in all_files:
        file_id = old_file.split('_')[-1].replace('.json', '')
        old_path = os.path.join(SOURCE_DIR, old_file)
        
        with open(old_path, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        clean_name = fix_lesson_name(plan_data['ders'], plan_data['sinif'], file_id)
        plan_data['ders'] = clean_name
        
        slug = slugify(clean_name)
        new_file = f"grade_{plan_data['sinif']}_{slug}_{file_id}.json"
        new_path = os.path.join(SOURCE_DIR, new_file)
        
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
            
        if old_file != new_file:
            os.remove(old_path)
            
        display_grade = "Hazırlık" if str(plan_data['sinif']) == "0" else str(plan_data['sinif'])
        new_idx_list.append({
            "dosya": new_file,
            "sinif": display_grade,
            "ders": clean_name,
            "kayit_sayisi": len(plan_data['plan'])
        })

    # Sort index
    new_idx_list.sort(key=lambda x: (
        -1 if x['sinif'] == "Hazırlık" else (int(x['sinif']) if x['sinif'].isdigit() else 999), 
        x['ders']
    ))

    new_idx_data = {"toplam": len(new_idx_list), "dosyalar": new_idx_list}
    with open(os.path.join(SOURCE_DIR, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(new_idx_data, f, ensure_ascii=False, indent=2)

    print(f"Index built with {len(new_idx_list)} files.")

    print("Mirroring to all directories...")
    for target in [DATA_DIR, os.path.join(BASE_DIR, "data/json_planlar")]:
        if not os.path.exists(target): os.makedirs(target)
        for f in os.listdir(target):
            if f.endswith(".json"): os.remove(os.path.join(target, f))
        for f in os.listdir(SOURCE_DIR):
            shutil.copy2(os.path.join(SOURCE_DIR, f), target)

    print("\nDONE! All 716+ files synchronized.")

if __name__ == "__main__":
    run_sync()
