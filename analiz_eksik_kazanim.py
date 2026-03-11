import os
import json

# Settings
JSON_DIR = "json_planlar"

def check_empty_kazanim(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "plan" not in data or not data["plan"]:
            return True, "Plan verisi yok"
        
        empty_rows = 0
        total_rows = len(data["plan"])
        
        for entry in data["plan"]:
            if "KAZANIM" not in entry or not entry["KAZANIM"] or str(entry["KAZANIM"]).strip() == "":
                empty_rows += 1
        
        if empty_rows == total_rows:
            return True, "Tüm kazanımlar boş"
        elif empty_rows > 0:
            return True, f"{empty_rows}/{total_rows} kazanım boş"
            
        return False, ""
    except Exception as e:
        return True, f"Hata: {e}"

def main():
    files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json") and f != "index.json"]
    print(f"{len(files)} JSON dosyası kontrol ediliyor...")
    
    empty_files = []
    for file_name in files:
        file_path = os.path.join(JSON_DIR, file_name)
        is_empty, reason = check_empty_kazanim(file_path)
        if is_empty:
            empty_files.append({"dosya": file_name, "neden": reason})

    if empty_files:
        print(f"\n{len(empty_files)} dosyada boş/eksik kazanım tespit edildi:")
        for item in empty_files:
            print(f"- {item['dosya']}: {item['neden']}")
        
        # Sonuçları bir dosyaya kaydet
        with open("eksik_kazanimlar.json", "w", encoding="utf-8") as f:
            json.dump(empty_files, f, ensure_ascii=False, indent=2)
    else:
        print("\nHiçbir dosyada boş kazanım tespit edilmedi. Tüm dosyalar dolu görünüyor.")

if __name__ == "__main__":
    main()
