import os
import docx
import json
import re

# Settings
WORD_DIR = "word_planlar"

# Turkish character restoration and cleaning logic (from json_yapici.py)
CHAR_FIX_MAP = {
    "BLGS": "BİLGİSİ", "BLGSI": "BİLGİSİ", "BLGLER": "BİLGİLER",
    "SSTEM": "SİSTEM", "SSTEMLER": "SİSTEMLER", "SSTEMNDE": "SİSTEMİNDE",
    "TEKNOLOJS": "TEKNOLOJİSİ", "TEKNOLOJLER": "TEKNOLOJİLER",
    "TEKNKLER": "TEKNİKLER", "TEKNKLERÎ": "TEKNİKLERİ",
    "TEKNK": "TEKNİK", "EĞTM": "EĞİTİM", "ÖĞRETM": "ÖĞRETİM",
    "YILLIK": "YILLIK", "PLANI": "PLANI", "ATÖLYES": "ATÖLYESİ",
    "GVENLK": "GÜVENLİK", "GVENLĞ": "GÜVENLİĞİ", "KLTR": "KÜLTÜR",
    "KLTRS": "KÜLTÜRÜ", "MEDENYET": "MEDENİYETİ", "HZMETLER": "HİZMETLER",
    "YYECEK": "YİYECEK", "TKEṪĊ": "TÜKETİCİ", "SEÇMEL": "SEÇMELİ",
    "MESLEK": "MESLEKİ", "ÜNTELENDİRLMİŞ": "ÜNİTELENDİRİLMİŞ",
    "ELEKTRK": "ELEKTRİK", "ELEKTRONK": "ELEKTRONİK", "MAKNE": "MAKİNE",
    "MUHASEBE": "MUHASEBE", "YAZILIM": "YAZILIM", "İNGLZCE": "İNGİLİZCE",
    "TARH": "TARİH", "TRKÇE": "TÜRKÇE", "EDEBYAT": "EDEBİYAT",
    "MZK": "MÜZİK", "BEDEN": "BEDEN", "FZK": "FİZİK", "BYOLOJ": "BİYOLOJİ",
    "COĞRFYA": "COĞRAFYA", "FELSEFE": "FELSEFE", "ALMANCA": "ALMANCA"
}

def fix_turkish_chars(text):
    if not text: return text
    result = text
    for corrupted, correct in sorted(CHAR_FIX_MAP.items(), key=lambda x: -len(x[0])):
        result = re.sub(r'\b' + re.escape(corrupted) + r'\b', correct, result)
    return result

def tr_clean(text):
    if not text: return "bilinmeyen"
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    result = str(text).translate(tr_map)
    result = re.sub(r'[^a-zA-Z0-9_]', '', result)
    result = re.sub(r'_+', '_', result).strip('_').lower()
    return result if result else "bilinmeyen"

def extract_info_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        sinif, ders = "bilinmeyen", "bilinmeyen"
        for table in doc.tables:
            if not table.rows: continue
            title_text = table.rows[0].cells[0].text.strip().upper()
            title_text = re.sub(r'\s+', ' ', title_text)
            
            match_sinif = re.search(r'(\d+)\.?\s*SINIF', title_text)
            if match_sinif: sinif = match_sinif.group(1)
            
            match_ders = re.search(r'SINIF\s+(.+?)\s+DERS\b', title_text)
            if not match_ders:
                match_ders = re.search(r'SINIF\s+(.+?)\s+ÜN.?TELEND', title_text)
            
            if match_ders:
                ders = fix_turkish_chars(match_ders.group(1).strip())
                ders = re.sub(r'\.{2,}', '', ders).strip()
                break
        return sinif, ders
    except: return "bilinmeyen", "bilinmeyen"

def main():
    files = [f for f in os.listdir(WORD_DIR) if f.endswith(".docx")]
    print(f"{len(files)} dosya işleniyor...")
    
    renamed_count = 0
    for file_name in files:
        # Skip files already renamed
        if file_name.startswith("grade_"): continue
        
        file_path = os.path.join(WORD_DIR, file_name)
        sinif, ders = extract_info_from_docx(file_path)
        
        file_id = os.path.splitext(file_name)[0].replace("plan_", "")
        sinif_clean = tr_clean(sinif)
        ders_clean = tr_clean(ders)
        
        new_name = f"grade_{sinif_clean}_{ders_clean}_{file_id}.docx"
        new_path = os.path.join(WORD_DIR, new_name)
        
        if file_path != new_path:
            os.rename(file_path, new_path)
            renamed_count += 1
            if renamed_count % 50 == 0:
                print(f"  {renamed_count} dosya adlandırıldı...")

    print(f"Tamamlandı! {renamed_count} dosya yeniden adlandırıldı.")

if __name__ == "__main__":
    main()
