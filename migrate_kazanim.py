import os
import json
import re

BASE_DIR = "/home/fatih/Masaüstü/Yıllık Planlar"
DATA_DIR = os.path.join(BASE_DIR, "json_planlar")

def migrate():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json") and f != "index.json"]
    total = len(files)
    print(f"Starting migration for {total} files...")
    
    for i, file_name in enumerate(files):
        file_path = os.path.join(DATA_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        modified = False
        for entry in data.get("plan", []):
            unite = entry.get("ÜNİTE", "").strip()
            konu = entry.get("KONU", "").strip()
            kazanim_text = entry.get("KAZANIM", "").strip()
            not_text = entry.get("BELİRLİ GÜN VE HAFTALAR", "").strip()
            
            # Construct new descriptive structure
            new_kazanim = f"Ünite/Tema: {unite if unite else '-'}\n"
            new_kazanim += f"Konu/İçerik: {konu if konu else '-'}\n"
            new_kazanim += f"Kazanım/Öğrenme Çıktıları: {kazanim_text if kazanim_text else '-'}"
            
            if not_text:
                new_kazanim += f"\nNot: {not_text}"
            
            entry["KAZANIM"] = new_kazanim
            modified = True
        
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        if (i+1) % 100 == 0:
            print(f"  Processed {i+1}/{total}")

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
