import docx
import os
import re

def fix_turkish_chars(text):
    return text # Simplified for debug

def find_header_map(row_cells_text):
    header_map = {}
    kazanim_cols = []
    
    for idx, cell_text in enumerate(row_cells_text):
        ct = cell_text.strip().upper()
        print(f"      Checking header cell {idx}: '{ct}'")
        if "AY" in ct and len(ct) < 20:
            header_map["AY"] = idx
            print(f"        -> Matched AY")
        elif "HAFTA" in ct and len(ct) < 25:
            header_map["HAFTA"] = idx
            print(f"        -> Matched HAFTA")
        elif "SAAT" in ct and len(ct) < 15:
            header_map["SAAT"] = idx
            print(f"        -> Matched SAAT")
        elif any(k in ct for k in ["ÜNİTE", "UNITE", "ÜNTE", "TEMA", "ÖĞRENME ALANI"]):
            header_map["ÜNİTE"] = idx
            print(f"        -> Matched ÜNİTE")
        elif "KONU" in ct and "AÇIKLAMA" not in ct:
            header_map["KONU"] = idx
            print(f"        -> Matched KONU")
        elif any(k in ct for k in ["KAZANIM", "ÖĞRENME ÇIKTI", "OGRENME CIKTI", "ETKİNLİK", "AÇIKLAMA", "BECERİ", "SÜREÇ BİLEŞEN"]):
            kazanim_cols.append(idx)
            print(f"        -> Matched KAZANIM_COL")
        elif any(k in ct for k in ["BELİRLİ GÜN", "HAFTALAR"]):
            header_map["BELİRLİ GÜN VE HAFTALAR"] = idx
            print(f"        -> Matched BELİRLİ GÜN")
            
    if kazanim_cols:
        header_map["KAZANIM_COLS"] = kazanim_cols
        
    return header_map

def debug_parse(file_path):
    print(f"Parsing {file_path}")
    doc = docx.Document(file_path)
    for t_idx, table in enumerate(doc.tables):
        print(f"  Table {t_idx} (rows: {len(table.rows)}):")
        header_map = {}
        header_row_idx = -1
        
        for i, row in enumerate(table.rows[:10]):
            row_text = [cell.text.strip() for cell in row.cells]
            row_upper = [t.upper() for t in row_text]
            
            common_keywords = ["AY", "HAFTA", "SAAT", "KONU", "KAZANIM", "ÜNİTE", "TEMA", "ÖĞRENME ÇIKTI"]
            match_count = 0
            for item in row_upper:
                if any(k in item for k in common_keywords):
                    match_count += 1
            
            print(f"    Row {i} match_count: {match_count}")
            if match_count >= 2:
                header_map = find_header_map(row_text)
                print(f"    Header Map: {header_map}")
                if len(header_map) >= 2:
                    header_row_idx = i
                    print(f"    Found header at row {i}")
                    break
        
        if header_row_idx != -1:
            print(f"    Extracting data from row {header_row_idx + 1} onwards...")
            for row_idx in range(header_row_idx + 1, min(header_row_idx + 5, len(table.rows))):
                cells = table.rows[row_idx].cells
                entry = {}
                row_vals = []
                for k_idx in range(len(cells)):
                    row_vals.append(cells[k_idx].text.strip().replace("\n", " "))
                print(f"      Row {row_idx} values: {row_vals}")

file_to_debug = "word_planlar/grade_9_trk_dl_ve_edebyati_hazirlik_811.docx"
debug_parse(file_to_debug)

file_to_debug_2 = "word_planlar/grade_5_matematk_uygulamalari_204.docx"
debug_parse(file_to_debug_2)
