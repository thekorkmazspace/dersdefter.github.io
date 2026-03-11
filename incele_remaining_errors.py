import docx
import os

files_to_check = [
    "grade_5_matematk_uygulamalari_204.docx",
    "grade_5_turkce_meb_1699.docx",
    "grade_9_cografya_sbl_1691.docx",
    "grade_9_trk_dl_ve_edebyati_hazirlik_811.docx"
]

WORD_DIR = "word_planlar"

for file_name in files_to_check:
    file_path = os.path.join(WORD_DIR, file_name)
    if not os.path.exists(file_path):
        # Maybe it has a different name
        print(f"Hata: {file_name} bulunamadı.")
        continue
        
    print(f"\n--- {file_name} ---")
    try:
        doc = docx.Document(file_path)
        for t_idx, table in enumerate(doc.tables):
            print(f"Table {t_idx} (rows: {len(table.rows)}):")
            for i, row in enumerate(table.rows[:10]):
                row_text = [cell.text.strip() for cell in row.cells]
                print(f"  Row {i}: {row_text}")
    except Exception as e:
        print(f"Hata: {e}")
