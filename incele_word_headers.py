import docx
import os

files_to_check = [
    "grade_8_bilisim_teknolojiler_ve_yazilim_secmeli_141.docx",
    "grade_8_dn_kultur_ve_ahlak_bilgisi_154.docx",
    "grade_9_sinif_rehberlk_432.docx",
    "grade_8_tc_inkilap_tarih_ve_atatrkclk_180.docx"
]

WORD_DIR = "word_planlar"

for file_name in files_to_check:
    file_path = os.path.join(WORD_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Hata: {file_name} bulunamadı.")
        continue
        
    print(f"\n--- {file_name} ---")
    try:
        doc = docx.Document(file_path)
        for table in doc.tables:
            for i, row in enumerate(table.rows[:5]):
                row_text = [cell.text.strip() for cell in row.cells]
                print(f"Row {i}: {row_text}")
    except Exception as e:
        print(f"Hata: {e}")
