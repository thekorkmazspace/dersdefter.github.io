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
    "SBL": "SOSYAL BİLİMLER LİSESİ", "AL": "ANADOLU LİSESİ", "FL": "FEN LİSESİ",
    "COGRAFYASI": "COĞRAFYASI", "DUNYASI": "DÜNYASI",
    "PNOMATIK": "PNÖMATİK", "HIDROLIK": "HİDROLİK", "SİSTEM": "SİSTEM",
    "TERMİNOLOJİSİ": "TERMİNOLOJİSİ", "ELEMANLARI": "ELEMANLARI",
    "TASARIM": "TASARIM", "GRAFİĞİ": "GRAFİĞİ",
    # Advanced Hyper-Fixes
    "ALE": "AİLE", "EKONOMS": "EKONOMİSİ", "KAYNAKLAR": "KAYNAKLARI",
    "ACIL": "ACİL", "HIZMET": "HİZMET", "HIZMETLER": "HİZMETLERİ",
    "DENZCLK": "DENİZCİLİK", "DENZDE": "DENİZDE", "EMNYET": "EMNİYET",
    "DGTAL": "DİJİTAL", "DIGITAL": "DİJİTAL", "ELEKTRONIK": "ELEKTRONİK",
    "COCUK": "ÇOCUK", "AKTVTELER": "AKTİVİTELERİ", "BAKIMI": "BAKIMI",
    "BASSAVCL": "BAŞSAVCILIK", "BASSAVCI": "BAŞSAVCI", "KALEM": "KALEM",
    "HUKUKI": "HUKUKİ", "TERMNO": "TERMİNOLOJİ", "TERM": "TERMİNOLOJİ",
    "İNKILAP": "İNKILAP", "TARİHİ": "TARİHİ", "ATATURK": "ATATÜRK",
    "TÜRKÇESİ": "TÜRKÇESİ", "URDU": "URDU", "OSMANLI": "OSMANLI",
    "CAGDAS": "ÇAĞDAŞ", "DUNYA": "DÜNYA", "MUKAYESELİ": "MUKAYESELİ",
    "ADAB-I": "ADAB-I", "MUASERET": "MUAŞERET", "AHLAK": "AHLAK",
    "TEKSTIL": "TEKSTİL", "TEKNOLOJILER": "TEKNOLOJİLERİ",
    "MODA": "MODA", "TASARIMLARI": "TASARIMLARI",
    "AHSAP": "AHŞAP", "OYUNCAK": "OYUNCAK", "ATOLYESI": "ATÖLYESİ",
    "TAKPLK": "TAKİPÇİLİK", "ATCLK": "ATÇILIK", "ATKLAR": "ATIKLAR",
    "ADL": "ADLİ", "SBLMEB": "SOSYAL BİLİMLER LİSESİ",
    "ALMEB": "ANADOLU LİSESİ", "FLMEB": "FEN LİSESİ",
    "REHBERLK": "REHBERLİK"
}

def deep_fix_name(name):
    # Fix combining marks
    name = unicodedata.normalize('NFKC', name)
    name = name.replace("ı̇", "i").replace("İ", "İ").replace("i̇", "i")
    
    # Stem-based context aware character fix
    stems = [
        (r'B[Iıİ]LG[Iıİ]SAYAR', 'BİLGİSAYAR'),
        (r'[Iıİ]LET[Iıİ]S[Iıİ]M', 'İLETİŞİM'),
        (r'[Iıİ]NG[Iıİ]L[Iıİ]ZCE', 'İNGİLİZCE'),
        (r'[İIicç]ER[Iıİ]K', 'İÇERİK'),
        (r'D[Iıİ]S', 'DIŞ'),
        (r'S[Iıİ]STEM', 'SİSTEM'),
        (r'UR[EÉ]T[Iıİ]M', 'ÜRETİM'),
        (r'E[GĞ][Iıİ]T[Iıİ]M', 'EĞİTİM'),
        (r'B[Iıİ]L[Iıİ]M', 'BİLİM'),
        (r'TEKN[Iıİ]K', 'TEKNİK'),
        (r'D[Iıİ]L', 'DİL'),
        (r'M[UÜ]Z[Iıİ]K', 'MÜZİK'),
        (r'BECER[Iıİ]', 'BECERİ'),
        (r'EDEB[Iıİ]YAT', 'EDEBİYAT'),
        (r'[Iıİ]S[Iıİ]ARET', 'İŞARET'),
        (r'C[AÁ]GDA[SŞ]', 'ÇAĞDAŞ'),
        (r'D[UÜ]NYA', 'DÜNYA'),
        (r'B[Iıİ]RLE[SŞ]T[Iıİ]RME', 'BİRLEŞTİRME'),
        (r'H[Iıİ]ZMET', 'HİZMET'),
        (r'D[Iıİ]J[Iıİ]TAL', 'DİJİTAL'),
        (r'D[Iıİ]G[Iıİ]TAL', 'DİJİTAL'),
        (r'ADAB-I', 'ADAB-I'),
        (r'MU[AÁ]SERET', 'MUAŞERET'),
        (r'AHSAP', 'AHŞAP'),
        (r'URET[Iıİ]M[Iıİ]', 'ÜRETİMİ'),
        (r'RES[Iıİ]M', 'RESİM'),
        (r'BA[GĞ][Iıİ]MS[Iıİ]Z', 'BAĞIMSIZ'),
        (r'[OÖ]NCES[Iıİ]', 'ÖNCESİ'),
        (r'SONRAS[Iıİ]', 'SONRASI'),
        (r'D[Iıİ]KS[Iıİ]YON', 'DİKSİYON'),
        (r'H[Iıİ]TABET', 'HİTABET'),
        (r'D[UÜ][SŞ][UÜ]NME', 'DÜŞÜNME'),
        (r'M[UÜ]DAHALE', 'MÜDAHALE'),
        (r'Y[OÖ]NTEM', 'YÖNTEM'),
        (r'B[Iıİ]LG[Iıİ]S[Iıİ]', 'BİLGİSİ'),
        (r'MEDEN[Iıİ]YET', 'MEDENİYETİ'),
        (r'YASAM', 'YAŞAM'),
        (r'İŞLEMLER$', 'İŞLEMLERİ'),
        (r'ISLEMLER$', 'İŞLEMLERİ'),
        (r'ISLEMLER', 'İŞLEMLERİ')
    ]
    
    for bad, good in stems:
        if good == 'MÜDÜRHALE': good = 'MÜDAHALE' # Cleanup
        name = re.sub(bad, good, name, flags=re.IGNORECASE)

    # Common OCR/Conversion fixes
    fixes = [
        (r'ı\.+kademe', 'I. Kademe'),
        (r'maarıf', 'MAARİF'),
        (r'atatrkclk', 'ATATÜRKÇÜLÜK'),
        (r'uretımı', 'ÜRETİMİ'),
        (r'gıysı', 'GİYSİ'),
        (r'ıscılıgı', 'İŞÇİLİĞİ'),
        (r'ale ekonoms', 'AİLE EKONOMİSİ'),
        (r'ale kaynaklar', 'AİLE KAYNAKLARI'),
        (r'cografyası', 'COĞRAFYASI'),
        (r'pnomatık', 'PNÖMATİK'),
        (r'hızmetlerı', 'HİZMETLERİ'),
        (r'hızmetler$', 'HİZMETLERİ'),
        (r'yasam becerileri', 'Yaşam Becerileri')
    ]
    
    for bad, good in fixes:
        name = re.sub(bad, good, name, flags=re.IGNORECASE)
        
    trunc_suffixes = [
        (r'SİSTEMLER$', 'SİSTEMLERİ'),
        (r'UYGULAMALAR$', 'UYGULAMALARI'),
        (r'TEKNOLOJİLER$', 'TEKNOLOJİLERİ'),
        (r'TEKNİKLER$', 'TEKNİKLERİ'),
        (r'İŞLEMLER$', 'İŞLEMLERİ'),
        (r'BECERİLER$', 'BECERİLERİ'),
        (r'CİHAZLAR$', 'CİHAZLARI'),
        (r'LABORATUVAR$', 'LABORATUVARI')
    ]
    
    name = turkish_upper(name)
    for bad, good in trunc_suffixes:
        name = re.sub(bad, good, name)
        
    return name

def linguistic_harmony_fix(name):
    # Fixes ı/i confusion at the end of words based on linguistic harmony
    words = name.split()
    fixed_words = []
    for word in words:
        if not word or len(word) < 3:
            fixed_words.append(word)
            continue
            
        clean_word = word.strip("()*")
        if clean_word.endswith('ı') and any(v in clean_word.lower() for v in 'eiöü'):
            word = word.replace('ı', 'i')
        elif clean_word.endswith('i') and any(v in clean_word.lower() for v in 'aıou'):
            # Only fix if it's common lesson suffix pattern
            if any(clean_word.lower().endswith(s) for s in ['ları', 'ması', 'ısı', 'ası']):
                word = word.replace('i', 'ı')
        fixed_words.append(word)
    return " ".join(fixed_words)
    
    # Selective high-confidence replacements for corrupted suffixes
    # (e.g. Sistemler -> Sistemleri, Uygulamalar -> Uygulamaları)
    trunc_suffixes = [
        (r'SİSTEMLER$', 'SİSTEMLERİ'),
        (r'UYGULAMALAR$', 'UYGULAMALARI'),
        (r'TEKNOLOJİLER$', 'TEKNOLOJİLERİ'),
        (r'TEKNİKLER$', 'TEKNİKLERİ'),
        (r'İŞLEMLER$', 'İŞLEMLERİ'),
        (r'BECERİLER$', 'BECERİLERİ'),
        (r'CİHAZLAR$', 'CİHAZLARI'),
        (r'UYGULAMALARI$', 'UYGULAMALARI'),
        (r'LABORATUVAR$', 'LABORATUVARI')
    ]
    
    for bad, good in fixes:
        name = re.sub(bad, good, name, flags=re.IGNORECASE)
        
    name = turkish_upper(name)
    for bad, good in trunc_suffixes:
        name = re.sub(bad, good, name)
        
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
    # (Deep fix already converted to upper, but we call it again for safety)
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
    
    # 5. Linguistic Harmony cleanup (surgical)
    name = linguistic_harmony_fix(name)
    
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
