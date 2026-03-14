#!/usr/bin/env python3
import os, json, re, shutil

# Base path
BASE_DIR = "/home/fatih/Masaüstü/Yıllık Planlar"
SOURCE_DIR = os.path.join(BASE_DIR, "json_planlar")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_JP_DIR = os.path.join(BASE_DIR, "data/json_planlar")

OFFICIAL_MATCHES = {
    "1949": "Beden Eğitimi ve Oyun (MEB)-1",
    "232": "Görsel Sanatlar-1",
    "1428": "Müzik(Maarif*)-1",
    "1539": "Serbest Etkinlikler-1",
    "1622": "Matematik (MEB)-1",
    "1697": "Türkçe (MEB)-1",
    "1669": "Hayat Bilgisi (MEB)-1",
    "1953": "Görsel Sanatlar (MEB)-1",
}

RESTORATION_MAP = {
    "ETKNLK": "ETKİNLİK", "ETKNLKLER": "ETKİNLİKLER",
    "SNF": "SINIF", "MAARF": "MAARİF",
    "MATEMATK": "MATEMATİK", "BLM": "BİLİM",
    "DN": "DİN", "TURKCE": "TÜRKÇE", "TRKCE": "TÜRKÇE",
    "GORSEL": "GÖRSEL", "SANATLARE": "SANATLAR",
    "UYGULAMAYEN": "UYGULAMALARI (YENİ*)",
    "UYGULAMALARIYEN": "UYGULAMALARI (YENİ*)",
    "UYGULAMALARI(YEN*)": "UYGULAMALARI (YENİ*)",
    "ELEKTRK": "ELEKTRİK", "ELEKTRONK": "ELEKTRONİK", "ELEKTROṄK": "ELEKTRONİK",
    "TEKNOLOJS": "TEKNOLOJİSİ", "TEKNOLOJLER": "TEKNOLOJİLER",
    "İNGİLİZCE": "İNGİLİZCE",
    "CHAZ": "CİHAZ", "SISTEM": "SİSTEM",
}

def fix_lesson_name(name, grade, file_id):
    if str(file_id) in OFFICIAL_MATCHES:
        return OFFICIAL_MATCHES[str(file_id)]
    name = name.upper()
    for bad, good in RESTORATION_MAP.items():
        name = re.sub(r'\b' + re.escape(bad) + r'\b', good, name)
    name = name.replace("UYGULAMA(YEN*)", "UYGULAMALARI (YENİ*)")
    name = name.replace("UYGULAMAYEN", "UYGULAMALARI (YENİ*)")
    if len(name) > 100: name = name[:97] + "..."
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
            
        new_idx_list.append({
            "dosya": new_file,
            "sinif": str(plan_data['sinif']),
            "ders": clean_name,
            "kayit_sayisi": len(plan_data['plan'])
        })

    # Sort index
    new_idx_list.sort(key=lambda x: (int(x['sinif']) if x['sinif'].isdigit() else 999, x['ders']))

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
