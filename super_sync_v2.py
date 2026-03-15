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

def turkish_upper(text):
    if not text: return ""
    return text.replace('i', 'İ').replace('ı', 'I').upper()

def turkish_lower(text):
    if not text: return ""
    return text.replace('İ', 'i').replace('I', 'ı').lower()

def turkish_title(text):
    if not text: return ""
    def fix_word(w):
        if not w: return ""
        return turkish_upper(w[0]) + turkish_lower(w[1:])
    
    return " ".join(fix_word(w) for w in text.split())

RESTORATION_MAP = {
    # Frequency Fixes
    "MAARIF": "MAARİF", "MAARF": "MAARİF",
    "BILGISI": "BİLGİSİ", "BILGI": "BİLGİ", "BILGILERI": "BİLGİLERİ",
    "DKAB": "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ", "DIN": "DİN",
    "KULTURU": "KÜLTÜRÜ", "KULTUR": "KÜLTÜR",
    "DILI": "DİLİ", "EDEBİYATI": "EDEBİYATI", "EDEBYATI": "EDEBİYATI",
    "TURK": "TÜRK", "TRK": "TÜRK",
    "INGILIZCE": "İNGİLİZCE", "ING": "İNGİLİZCE",
    "MATEMATIK": "MATEMATİK", "MAT": "MATEMATİK",
    "FIZIK": "FİZİK", "FZK": "FİZİK",
    "BIYOLOJI": "BİYOLOJİ", "BYL": "BİYOLOJİ",
    "KIMYA": "KİMYA", "KMY": "KİMYA",
    "GORSEL": "GÖRSEL", "SANATLAR": "SANATLAR",
    "MUZIK": "MÜZİK", "MZK": "MÜZİK",
    "BEDEN": "BEDEN", "EGT": "EĞİTİMİ", "EGITIMI": "EĞİTİMİ",
    "REHBERLK": "REHBERLİK", "REHBERLIK": "REHBERLİK",
    "BECERILERI": "BECERİLERİ", "BECERI": "BECERİ",
    "ILETISIM": "İLETİŞİM", "ILETISM": "İLETİŞİM",
    "GMDSS": "GMDSS", "TEKNK": "TEKNİK", "TEKNIK": "TEKNİK",
    "SISTEMLERI": "SİSTEMLERİ", "SISTEMLER": "SİSTEMLER", "SISTEMI": "SİSTEMİ",
    "UYGULAMALARI": "UYGULAMALARI", "UYGULAMA": "UYGULAMA",
    "ANATOMI": "ANATOMİ", "FIZYOLOJI": "FİZYOLOJİ",
    "HAZIRLIK": "HAZIRLIK", "HZL": "HAZIRLIK",
    "OZEL": "ÖZEL", "EGITIM": "EĞİTİM",
    "MESLEKI": "MESLEKİ", "GELISIM": "GELİŞİM",
    "COGRAFYA": "COĞRAFYA", "TARİH": "TARİH", "TARIH": "TARİH",
    "INKILAP": "İNKILAP", "ATATURKCULUK": "ATATÜRKÇÜLÜK",
    "SAGLIK": "SAĞLIK", "GUVENLIK": "GÜVENLİK",
    "ISARET": "İŞARET", "TOPLUMSAL": "TOPLUMSAL", "UYUM": "UYUM",
    "BECERILER": "BECERİLER", "BECERISI": "BECERİSİ",
    "AHSAP": "AHŞAP", "ATOLYESI": "ATÖLYESİ", "ATOLYE": "ATÖLYE",
    "YONLENDIRME": "YÖNLENDİRME", "YONETICILIGI": "YÖNETİCİLİĞİ",
    "GIRISIMCILIK": "GİRİŞİMCİLİK", "AHILIK": "AHİLİK",
    "URETIMI": "ÜRETİMİ", "URETIM": "ÜRETİM", "GIYSI": "GİYSİ",
    "TASARIMI": "TASARIMI", "SAYISAL": "SAYISAL", "MANTIK": "MANTIK",
    "TEKNOLOJISI": "TEKNOLOJİSİ", "TEKNOLOJILERI": "TEKNOLOJİLERİ",
    "TESSAT": "TESİSAT", "Tesisati": "TESİSATI",
    "YAPI": "YAPI", "ELEKTRIK": "ELEKTRİK", "KUVVET": "KUVVET",
    "OTOMASYON": "OTOMASYON", "GUC": "GÜÇ", "ELEKTRONIGI": "ELEKTRONİĞİ",
    "BILGISAYAR": "BİLGİSAYAR", "DESTEKLI": "DESTEKLİ", "CİZİM": "ÇİZİM",
    "CIHAZ": "CİHAZ", "CIHAZLARI": "CİHAZLARI", "GRAFIK": "GRAFİK",
    "MMAR": "MİMARİ", "MOBILYA": "MOBİLYA", "İC": "İÇ", "MEKAN": "MEKAN",
    "SİSTEMİNDE": "SİSTEMİNDE", "İLK": "İLK", "YARDIM": "YARDIM",
    "FELSEFE": "FELSEFE", "ALMANCA": "ALMANCA", "COĞRAFYA": "COĞRAFYA",
    "EDEBYAT": "EDEBİYAT", "EDB": "EDEBİYAT", "TRKCE": "TÜRKÇE",
    "BILISIM": "BİLİŞİM", "İC": "İÇ", "DİSYON": "DİKSİYON",
    "SBL": "SOSYAL BİLİMLER LİSESİ", "AL": "ANADOLU LİSESİ", "FL": "FEN LİSESİ"
}

def deep_fix_name(name):
    # Fix character level corruption before mapping
    fixes = [
        (r'DıL', 'DİL'), (r'BıLG', 'BİLG'), (r'ıLETıS', 'İLETİŞ'),
        (r'ıNGıLıZ', 'İNGİLİZ'), (r'MATEMATıK', 'MATEMATİK'),
        (r'MuzıK', 'MÜZİK'), (r'BıRıNCı', 'BİRİNCİ'), (r'ıkıncı', 'İKİNCİ'),
        (r'ııı', 'III'), (r'ıı', 'II'), (r'ı\.+kademe', 'I. Kademe'),
        (r'maarıf', 'MAARİF'), (r'BECERı', 'BECERİ'), (r'SıSTEM', 'SİSTEM'),
        (r'SıNF', 'SINIF'), (r'EDEBıYAT', 'EDEBİYAT'), (r'eğıtım', 'EĞİTİM'),
        (r'ıŞaret', 'İŞARET'), (r'ıletıŞım', 'İLETİŞİM'), (r'ıÇerık', 'İÇERİK'),
        (r'ıle', 'İLE'), (r'etkınlık', 'ETKİNLİK'),
        (r'ıbadet', 'İBADET'), (r'ınanc', 'İNANÇ'), (r'ıslam', 'İSLAM'),
        (r'tıcaret', 'TİCARET'), (r'ısletme', 'İŞLETME'), (r'ıletısım', 'İLETİŞİM'),
        (r'fızık', 'FİZİK'), (r'bıyolojı', 'BİYOLOJİ'), (r'kımya', 'KİMYA'),
        (r'dzayn', 'DİZAYN'), (r'grafık', 'GRAFİK'), (r'resem', 'RESİM'),
        (r'teknık', 'TEKNİK'), (r'hukukı', 'HUKUKİ'), (r'takplk', 'TAKİPÇİLİK'),
        (r'clık', 'CILIK'), (r'clıgı', 'CILIĞI'), (r'atatrkclk', 'ATATÜRKÇÜLÜK'),
        (r'osmanlı turkcesı', 'OSMANLI TÜRKÇESİ'), (r'inkılap tarıh', 'İNKILAP TARİHİ'),
        (r'termınolojı', 'TERMİNOLOJİ'), (r'haberlesme', 'HABERLEŞME'),
        (r'emnyet', 'EMNİYET'), (r'uretımı', 'ÜRETİMİ'), (r'gıysı', 'GİYSİ'),
        (r'teknolojı', 'TEKNOLOJİ'), (r'sıstemlerı', 'SİSTEMLERİ'), (r'teknyen', 'TEKNİSYEN'),
        (r'ahılık', 'AHİLİK'), (r'abıyee', 'ABİYE'), (r'abıye', 'ABİYE'),
        (r'ıscılıgı', 'İŞÇİLİĞİ'), (r'ıscı', 'İŞÇİ'), (r'ısnın', 'İŞİNİN'),
        (r'sanatlar', 'SANATLAR'), (r'turk_cesı', 'TÜRKÇESİ')
    ]
    
    # Selective high-confidence replacements for corrupted suffixes
    # Only if not preceded by 'Hazırl' 'Sın' 'Bak' 'Anlat' 'Yap' 'Yaz'
    # Actually, let's stick to the word list for now to be safe, but more expanded.
    
    # Apply word-based fixes
    for bad, good in fixes:
        name = re.sub(bad, good, name, flags=re.IGNORECASE)
        
    return name

def fix_lesson_name(name, grade, file_id):
    # 0. Basic cleaning (strip combining marks if any, but safely)
    # Instead of full NFKD, let's just cleanup known artifacts
    name = name.replace("ı̇", "i").replace("İ", "İ").replace("i̇", "i").replace("i̇", "i")
    
    # 1. Use absolute truth from site if ID found
    if str(file_id) in OFFICIAL_NAMES:
        name = OFFICIAL_NAMES[str(file_id)]
    
    # 2. Pre-cleanup character corruption
    name = deep_fix_name(name)
    
    # 3. General restoration
    # Map back broken words to uppercase first for consistency
    name = turkish_upper(name)
    for bad, good in RESTORATION_MAP.items():
        name = re.sub(r'\b' + re.escape(bad) + r'\b', good, name)
    
    # 3. Strip noise
    name = re.sub(r'\(YEN.*\)', '', name)
    name = re.sub(r'\(MEB.*\)', '', name)
    name = re.sub(r'\(MESEM.*\)', '', name, flags=re.IGNORECASE)
    name = name.replace("UYGULAMA(YEN*)", "UYGULAMALARI").replace("UYGULAMAYEN", "UYGULAMALARI")
    
    # Strip grade suffixes like -0, -1, -9, -10, -11, -12
    name = re.sub(r'-\d+$', '', name).strip()
    
    # Final check for common mistakes
    if "TÜRK DİLİ EDEBİYATI" in name:
        name = name.replace("TÜRK DİLİ EDEBİYATI", "TÜRK DİLİ VE EDEBİYATI")
    if "MAARİF" in name:
        name = name.replace("MAARİF*", "MAARİF").replace("(MAARİF)", "MAARİF")
    
    # Clean up Roman numerals and cadres
    name = name.replace("I-ıı-ıı Kademe", "I-II-III. Kademe")
    name = name.replace("I-ıı-ııı Kademe", "I-II-III. Kademe")
    name = name.replace("I-ıı Kademe", "I-II. Kademe")
    
    # 4. Apply Title Case
    name = turkish_title(name)
    
    # Clean up excess spaces again
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
            if f.endswith(".json") and f != "official_names.json":
                os.remove(os.path.join(target, f))
        for f in os.listdir(SOURCE_DIR):
            shutil.copy2(os.path.join(SOURCE_DIR, f), target)

    print("\nDONE! All 716+ files synchronized.")

if __name__ == "__main__":
    run_sync()
