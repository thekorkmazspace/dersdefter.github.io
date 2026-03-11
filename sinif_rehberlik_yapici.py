import os
import docx
import json
import re

WORD_DIR = "sinif_rehberlik"
JSON_DIR = "sinif_rehberlik_json"

os.makedirs(JSON_DIR, exist_ok=True)

# Turkish character fix map (same as main script)
FIXES = {
    "BLŞM": "BİLİŞİM", "BLGSAYAR": "BİLGİSAYAR", "BLGSAYARLI": "BİLGİSAYARLI",
    "BLM": "BİLİM", "BLG": "BİLGİ", "BLGS": "BİLGİSİ", "DN": "DİN",
    "KLTR": "KÜLTÜR", "SSTEM": "SİSTEM", "SSTEMLER": "SİSTEMLER",
    "TEKNOLOJLER": "TEKNOLOJİLER", "TEKNKLER": "TEKNİKLER", "TEKNK": "TEKNİK",
    "TEKNOLOJ": "TEKNOLOJİ", "EĞTM": "EĞİTİM", "EĞTMDE": "EĞİTİMDE",
    "ATÖLYES": "ATÖLYESİ", "GVENLK": "GÜVENLİK", "SEÇMEL": "SEÇMELİ",
    "MESLEK": "MESLEKİ", "REHBERLK": "REHBERLİK", "GELŞM": "GELİŞİM",
    "GRAFĞ": "GRAFİĞİ", "GRAFK": "GRAFİK", "ÜRETM": "ÜRETİM",
    "ELEKTRK": "ELEKTRİK", "ELEKTRONK": "ELEKTRONİK", "MAKNE": "MAKİNE",
    "MAKNELER": "MAKİNELER", "CHAZLAR": "CİHAZLAR", "PERYODK": "PERİYODİK",
    "DGTAL": "DİJİTAL", "ENDSTRYEL": "ENDÜSTRİYEL", "ROBOTK": "ROBOTİK",
    "PSKOLOJ": "PSİKOLOJİ", "TRKÇE": "TÜRKÇE", "TRK": "TÜRK",
    "TARH": "TARİH", "SERVS": "SERVİS", "BECERLER": "BECERİLER",
    "KMYA": "KİMYA", "EDEBYATI": "EDEBİYATI", "EDEBYAT": "EDEBİYAT",
    "KARYER": "KARİYER", "YÖNLENDRME": "YÖNLENDİRME", "TRAFK": "TRAFİK",
    "DL": "DİL", "ETKNLKLER": "ETKİNLİKLER", "SNF": "SINIF",
    "FZK": "FİZİK", "BYOLOJ": "BİYOLOJİ", "SOSYOLOJ": "SOSYOLOJİ",
    "HZMETLER": "HİZMETLER", "MATEMATK": "MATEMATİK", "İNGLZCE": "İNGİLİZCE",
    "İŞLETM": "İŞLETİM", "SBER": "SİBER", "GYM": "GİYİM",
    "BNA": "BİNA", "TESSAT": "TESİSAT", "ÖLÇMLER": "ÖLÇÜMLER",
}

def fix_ders(text):
    if not text:
        return text
    words = text.split()
    return " ".join(FIXES.get(w, w) for w in words)

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
    if not table.rows:
        return sinif, ders
    title_text = table.rows[0].cells[0].text.strip().upper()
    title_text = re.sub(r'\s+', ' ', title_text)
    match_sinif = re.search(r'(\d+)\.?\s*SINIF', title_text)
    if match_sinif:
        sinif = match_sinif.group(1)
    match_ders = re.search(r'SINIF\s+(.+?)\s+DERS\b', title_text)
    if match_ders:
        ders = re.sub(r'\.{2,}', '', match_ders.group(1)).strip()
    if ders == "bilinmeyen":
        match2 = re.search(r'SINIF\s+(.+?)\s+ÜN.?TELEND', title_text)
        if match2:
            ders = re.sub(r'\.{2,}', '', match2.group(1)).strip()
    if ders != "bilinmeyen":
        ders = fix_ders(ders)
    return sinif, ders

def find_header_map(row_cells_text):
    header_map = {}
    for idx, cell_text in enumerate(row_cells_text):
        ct = cell_text.strip().upper()
        if ct == "AY":
            header_map["AY"] = idx
        elif ct == "HAFTA":
            header_map["HAFTA"] = idx
        elif ct == "SAAT":
            header_map["SAAT"] = idx
        elif "ÜNİTE" in ct or "ÜNTE" in ct:
            header_map["ÜNİTE"] = idx
        elif ct == "KONU":
            header_map["KONU"] = idx
        elif "KAZANIM" in ct and "AÇIKLAMA" in ct:
            header_map["KAZANIM AÇIKLAMASI"] = idx
        elif "KAZANIM" in ct:
            header_map["KAZANIM"] = idx
        elif "BELİRLİ" in ct or ("GÜN" in ct and "HAFTA" in ct):
            header_map["BELİRLİ GÜN VE HAFTALAR"] = idx
    return header_map

def parse_docx(file_path, file_name):
    try:
        doc = docx.Document(file_path)
        sinif, ders = "bilinmeyen", "bilinmeyen"
        all_data = []

        for table in doc.tables:
            header_map = {}
            header_row_idx = -1

            for i, row in enumerate(table.rows[:5]):
                row_text = [cell.text.strip() for cell in row.cells]
                row_upper = [t.upper() for t in row_text]
                if any(k in row_upper for k in ["AY", "HAFTA", "SAAT", "KONU", "KAZANIM"]):
                    header_map = find_header_map(row_text)
                    if len(header_map) >= 3:
                        header_row_idx = i
                        break

            if header_row_idx == -1:
                continue

            if header_row_idx > 0:
                s, d = extract_title_info(table)
                if s != "bilinmeyen":
                    sinif = s
                if d != "bilinmeyen":
                    ders = d

            for row_idx in range(header_row_idx + 1, len(table.rows)):
                cells = table.rows[row_idx].cells
                entry = {}
                has_val = False
                for key, col_idx in header_map.items():
                    if col_idx < len(cells):
                        val = cells[col_idx].text.strip()
                        if val:
                            entry[key] = val
                            has_val = True
                if has_val:
                    all_data.append(entry)

        # Fallback: extract sinif and ders from filename
        # e.g. sinif-rehberlik-5-plan.docx → sinif=5, ders="SINIF REHBERLİK"
        base = file_name.replace(".docx", "")
        parts = base.split("-")
        if sinif == "bilinmeyen":
            for p in parts:
                if p.isdigit():
                    sinif = p
                    break
        if ders == "bilinmeyen":
            # Build ders from filename words (not the grade number and not "plan")
            ders_parts = [p.upper() for p in parts if not p.isdigit() and p.lower() != "plan"]
            ders = " ".join(ders_parts)
            ders = fix_ders(ders)

        return {"sinif": sinif, "ders": ders, "plan": all_data}
    except Exception as e:
        print(f"  HATA ({file_name}): {e}")
        return None


def main():
    files = sorted([f for f in os.listdir(WORD_DIR) if f.endswith(".docx")])
    print(f"{len(files)} dosya bulundu. Dönüştürme başlıyor...")

    index = []
    count = 0
    errors = 0

    for file_name in files:
        file_path = os.path.join(WORD_DIR, file_name)
        result = parse_docx(file_path, file_name)

        if result and result["plan"]:
            sinif_clean = tr_clean(result["sinif"])
            ders_clean = tr_clean(result["ders"])
            # Use filename without extension as ID
            file_id = file_name.replace(".docx", "")
            output_name = f"grade_{sinif_clean}_{ders_clean}_{file_id}.json"
            output_path = os.path.join(JSON_DIR, output_name)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            index.append({
                "dosya": output_name,
                "sinif": result["sinif"],
                "ders": result["ders"],
                "kayit_sayisi": len(result["plan"])
            })
            count += 1
            print(f"  [{count}] {output_name}")
        else:
            errors += 1

    # Write sinif_index.json
    index_path = os.path.join(JSON_DIR, "sinif_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"toplam": count, "dosyalar": index}, f, ensure_ascii=False, indent=2)

    print(f"\nTamamlandı! {count} dosya + sinif_index.json oluşturuldu. ({errors} hatalı/boş)")


if __name__ == "__main__":
    main()
