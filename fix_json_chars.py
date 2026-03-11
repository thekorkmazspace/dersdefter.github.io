import os
import json
import re

# Settings
JSON_DIR = "json_planlar"

# Genişletilmiş Türkçe Karakter Düzeltme Haritası
CHAR_FIX_MAP = {
    "BLGSI": "BİLGİSİ", "BLGS": "BİLGİSİ", "BLGLER": "BİLGİLER",
    "SSTEM": "SİSTEM", "SSTEMLER": "SİSTEMLER", "SSTEMNDE": "SİSTEMİNDE",
    "TEKNOLOJS": "TEKNOLOJİSİ", "TEKNOLOJLER": "TEKNOLOJİLER",
    "TEKNKLER": "TEKNİKLER", "TEKNK": "TEKNİK",
    "EĞTM": "EĞİTİM", "ÖĞRETM": "ÖĞRETİM",
    "YILLIK": "YILLIK", "PLANI": "PLANI",
    "ATÖLYES": "ATÖLYESİ", "GVENLK": "GÜVENLİK", "GVENLĞ": "GÜVENLİĞİ",
    "KLTR": "KÜLTÜR", "KLTRS": "KÜLTÜRÜ", "MEDENYET": "MEDENİYETİ",
    "HZMETLER": "HİZMETLER", "YYECEK": "YİYECEK", "TKEṪĊ": "TÜKETİCİ",
    "SEÇMEL": "SEÇMELİ", "MESLEK": "MESLEKİ", "ÜNTELENDİRLMİŞ": "ÜNİTELENDİRİLMİŞ",
    "ELEKTRK": "ELEKTRİK", "ELEKTRONK": "ELEKTRONİK", "MAKNE": "MAKİNE",
    "MUHASEBE": "MUHASEBE", "YAZILIM": "YAZILIM", "İNGLZCE": "İNGİLİZCE",
    "TARH": "TARİH", "TRKÇE": "TÜRKÇE", "EDEBYAT": "EDEBİYAT",
    "MZK": "MÜZİK", "BEDEN": "BEDEN", "FZK": "FİZİK", "BYOLOJ": "BİYOLOJİ",
    "COĞRFYA": "COĞRAFYA", "FELSEFE": "FELSEFE", "ALMANCA": "ALMANCA",
    "DKSYON": "DİKSİYON", "HTABET": "HİTABET", "KERM": "KERİM", "AKAD": "AKAİD",
    "BLŞM": "BİLİŞİM", "İNKILAP": "İNKILAP", "ATATÜRKÇÜLÜK": "ATATÜRKÇÜLÜK",
    "AHLAK": "AHLAK", "KÜLTÜR": "KÜLTÜRÜ", # Sadece ders isminde Kültür varsa Kültürü yapar
}

# Özel tam eşleşme düzeltmeleri
FULL_MATCH_FIX = {
    "BEDEN EĞİTİM VE SPOR": "BEDEN EĞİTİMİ VE SPOR",
    "DİN KÜLTÜR VE AHLAK BİLGİSİ": "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ",
    "TÜRK DİL EDEBİYATI": "TÜRK DİLİ VE EDEBİYATI",
    "DİN KÜLTÜRE VE AHLAK BİLGİSİ": "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ",
    "KURAN'I KERM": "KUR'AN-I KERİM",
    "KURANI KERİM": "KUR'AN-I KERİM",
}

def fix_text(text):
    if not text or not isinstance(text, str):
        return text
    
    # Önce tam eşleşme kontrolü (case-insensitive)
    t_upper = text.upper()
    for bad, good in FULL_MATCH_FIX.items():
        if bad in t_upper:
            # Basit bir replace yeterli mi? Evet, çünkü tam ders isimleri genelde tekil.
            text = text.replace(bad, good).replace(bad.lower(), good.lower())
    
    # Sonra kelime kelime düzeltme
    for corrupted, correct in sorted(CHAR_FIX_MAP.items(), key=lambda x: -len(x[0])):
        # Kelime sınırlarına bakarak (word boundaries) değiştirme
        pattern = r'\b' + re.escape(corrupted) + r'\b'
        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
    
    return text

def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        changed = False
        
        # 'ders' alanını düzelt
        if "ders" in data:
            old_ders = data["ders"]
            new_ders = fix_text(old_ders)
            if old_ders != new_ders:
                data["ders"] = new_ders
                changed = True
        
        # 'plan' içindeki her bir kaydı düzelt
        if "plan" in data and isinstance(data["plan"], list):
            for entry in data["plan"]:
                for key, val in entry.items():
                    if isinstance(val, str):
                        new_val = fix_text(val)
                        if val != new_val:
                            entry[key] = new_val
                            changed = True
        
        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Hata {file_path}: {e}")
        return False

def main():
    files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json") and f != "index.json"]
    print(f"{len(files)} JSON dosyası taranıyor...")
    
    fixed_count = 0
    for file_name in files:
        file_path = os.path.join(JSON_DIR, file_name)
        if process_file(file_path):
            fixed_count += 1
            if fixed_count % 50 == 0:
                print(f"  {fixed_count} dosya düzeltildi...")
    
    print(f"Tamamlandı! {fixed_count} dosya güncellendi.")

if __name__ == "__main__":
    main()
