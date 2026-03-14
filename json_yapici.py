import os
import docx
import json
import re

# Settings
WORD_DIR = "word_planlar"
JSON_DIR = "json_planlar"

# ─── Turkish character restoration map ───
CHAR_FIX_MAP = {
    "BLGSAYAR": "BİLGİSAYAR", "BLG": "BİLGİ", "ÇZM": "ÇİZİM", "TESSAT": "TESİSAT",
    "CHAZ": "CİHAZ", "GRAFK": "GRAFİK", "MMAR": "MİMARİ", "STATK": "STATİK",
    "MOBLYA": "MOBİLYA", "RESM": "RESMİ", "DESTEKL": "DESTEKLİ", "CHAZLARI": "CİHAZLARI",
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
    "AHLAK": "AHLAK", "KÜLTÜR": "KÜLTÜRÜ", "ANALOG": "ANALOG"
}

FULL_MATCH_FIX = {
    "BEDEN EĞİTİM VE SPOR": "BEDEN EĞİTİMİ VE SPOR",
    "DİN KÜLTÜR VE AHLAK BİLGİSİ": "DİN KÜLTÜRÜ VE AHLAK BİLGİSİ",
    "TÜRK DİL EDEBİYATI": "TÜRK DİLİ VE EDEBİYATI",
    "KURAN'I KERM": "KUR'AN-I KERİM",
    "KURANI KERİM": "KUR'AN-I KERİM"
}

def fix_turkish_chars(text):
    if not text or not isinstance(text, str):
        return text
    t_upper = text.upper()
    for bad, good in FULL_MATCH_FIX.items():
        if bad in t_upper:
            text = text.replace(bad, good).replace(bad.lower(), good.lower())
    for corrupted, correct in sorted(CHAR_FIX_MAP.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(corrupted) + r'\b'
        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
    return text

def tr_clean(text):
    if not text:
        return "bilinmeyen"
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ ", "cgiosuCGIOSU_")
    result = str(text).translate(tr_map)
    result = re.sub(r'[^a-zA-Z0-9_]', '', result)
    result = re.sub(r'_+', '_', result).strip('_').lower()
    return result if result else "bilinmeyen"

def extract_title_info(table):
    sinif = "bilinmeyen"
    ders = "bilinmeyen"
    for row_idx in range(min(5, len(table.rows))):
        try:
            row_text = " ".join([c.text for c in table.rows[row_idx].cells]).upper()
        except: continue
        row_text = re.sub(r'\s+', ' ', row_text)
        match_sinif = re.search(r'(\d+)\.?\s*SINIF', row_text)
        if match_sinif and sinif == "bilinmeyen":
            sinif = match_sinif.group(1)
        match_ders = re.search(r'SINIF\s+(.+?)\s+DERS\b', row_text)
        if not match_ders:
            match_ders = re.search(r'SINIF\s+(.+?)\s+(ÜN.|UN.)TELEND', row_text)
        if not match_ders:
            match_ders = re.search(r'ALAN.?\s+(.+?)\s+(ÜN.|UN.)TELEND', row_text)
        if match_ders and ders == "bilinmeyen":
            ders_raw = match_ders.group(1).strip()
            ders_raw = re.sub(r'\.{2,}', '', ders_raw).strip()
            # Clean up redundant prefixes
            ders_raw = re.search(r'([A-ZÇĞİÖŞÜ].*)', ders_raw).group(1) if re.search(r'([A-ZÇĞİÖŞÜ].*)', ders_raw) else ders_raw
            if len(ders_raw) > 2:
                ders = ders_raw
    if ders != "bilinmeyen":
        ders = fix_turkish_chars(ders)
    return sinif, ders

def find_header_map(row_cells_text):
    header_map = {}
    kazanim_cols = []
    found_keys = set()
    
    for idx, cell_text in enumerate(row_cells_text):
        ct = cell_text.strip().upper()
        if "AY" in ct and len(ct) < 20 and "AY" not in found_keys:
            header_map["AY"] = idx
            found_keys.add("AY")
        elif "HAFTA" in ct and len(ct) < 25 and "HAFTA" not in found_keys:
            header_map["HAFTA"] = idx
            found_keys.add("HAFTA")
        elif "SAAT" in ct and len(ct) < 15 and "SAAT" not in found_keys:
            header_map["SAAT"] = idx
            found_keys.add("SAAT")
        elif any(k in ct for k in ["ÜNİTE", "UNİTE", "ÜNTE", "TEMA", "ÖĞRENME ALANI"]):
            header_map["ÜNİTE"] = idx
        elif "KONU" in ct and "AÇIKLAMA" not in ct:
            header_map["KONU"] = idx
        elif any(k in ct for k in ["KAZANIM", "ÖĞRENME ÇIKTI", "OGRENME CIKTI", "ETKİNLİK", "AÇIKLAMA", "BECERİ", "SÜREÇ BİLEŞEN"]):
            kazanim_cols.append(idx)
        elif any(k in ct for k in ["BELİRLİ GÜN", "HAFTALAR"]):
            header_map["BELİRLİ GÜN VE HAFTALAR"] = idx
            
    if kazanim_cols:
        header_map["KAZANIM_COLS"] = kazanim_cols
    return header_map

def parse_docx_to_json(file_path, file_name):
    try:
        doc = docx.Document(file_path)
        sinif, ders = "bilinmeyen", "bilinmeyen"
        all_data = []
        for table in doc.tables:
            best_header_idx = -1
            best_score = 0
            best_map = {}
            # Scoring headers in top 10 rows
            for i, row in enumerate(table.rows[:10]):
                try: row_text = [cell.text.strip().upper() for cell in row.cells]
                except: continue
                # Unique match scoring
                keywords = ["AY", "HAFTA", "SAAT", "KONU", "KAZANIM", "ÜNİTE", "TEMA", "ÖĞRENME ÇIKTI", "SÜREÇ BİLEŞEN"]
                score = sum(1 for k in keywords if any(k in t for t in row_text))
                if score > best_score:
                    best_score = score
                    best_header_idx = i
                    best_map = find_header_map(row_text)
            
            if best_header_idx == -1 or best_score < 2: continue
            
            # Use the best header row found
            header_map = best_map
            header_row_idx = best_header_idx
            
            s, d = extract_title_info(table)
            if s != "bilinmeyen": sinif = s
            if d != "bilinmeyen": ders = d

            for row_idx in range(header_row_idx + 1, len(table.rows)):
                try: cells = table.rows[row_idx].cells
                except: continue
                
                # Pre-define order for better readability (Ünite first)
                ordered_keys = ["ÜNİTE", "AY", "HAFTA", "SAAT", "KONU", "BELİRLİ GÜN VE HAFTALAR"]
                entry = {}
                has_val = False
                
                for key in ordered_keys:
                    col_idx = header_map.get(key)
                    if col_idx is not None and col_idx < len(cells):
                        val = cells[col_idx].text.strip()
                        if val:
                            entry[key] = fix_turkish_chars(val)
                            has_val = True
                
                # Handle KAZANIM separately at the end
                if "KAZANIM_COLS" in header_map:
                    kazanim_texts = []
                    for k_idx in header_map["KAZANIM_COLS"]:
                        if k_idx < len(cells):
                            val = cells[k_idx].text.strip()
                            if val: kazanim_texts.append(val)
                    if kazanim_texts:
                        unique_kazanims = []
                        for kt in kazanim_texts:
                            if not unique_kazanims or kt != unique_kazanims[-1]:
                                unique_kazanims.append(kt)
                        entry["KAZANIM"] = fix_turkish_chars("\n".join(unique_kazanims))
                        has_val = True
                
                if has_val: all_data.append(entry)

        if sinif == "bilinmeyen" or ders == "bilinmeyen":
            orig = file_name.replace(".docx", "")
            if ders == "bilinmeyen": ders = orig
        return {"sinif": sinif, "ders": ders, "plan": all_data}
    except Exception as e:
        print(f"  HATA ({file_name}): {e}")
        return None

def main():
    if os.path.exists(JSON_DIR):
        import shutil
        shutil.rmtree(JSON_DIR)
    os.makedirs(JSON_DIR, exist_ok=True)
    
    files = sorted([f for f in os.listdir(WORD_DIR) if f.endswith(".docx")])
    index = []
    count = 0
    for file_name in files:
        result = parse_docx_to_json(os.path.join(WORD_DIR, file_name), file_name)
        if result and result["plan"]:
            sinif_clean = tr_clean(result["sinif"])
            ders_clean = tr_clean(result["ders"])[:50] # Limit filename length
            
            # Extract ID more safely
            file_id = file_name.split("_")[-1].replace(".docx", "")
            output_name = f"grade_{sinif_clean}_{ders_clean}_{file_id}.json"
            output_path = os.path.join(JSON_DIR, output_name)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            index.append({"dosya": output_name, "sinif": result["sinif"], "ders": result["ders"], "kayit_sayisi": len(result["plan"])})
            count += 1
            if count % 100 == 0: print(f"  İşlenen: {count}/{len(files)}")
    with open(os.path.join(JSON_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"toplam": count, "dosyalar": index}, f, ensure_ascii=False, indent=2)
    print(f"\nBitti! {count} dosya oluşturuldu.")

if __name__ == "__main__":
    main()
