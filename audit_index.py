import json
import re

DATA_PATH = "/home/fatih/Masaüstü/Yıllık Planlar/data/index.json"

def audit():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    issues = {
        "tı_bı_dı": [], # Matches 'Dılı', 'Bılgısı'
        "turk_u": [], # Matches 'Turk' instead of 'Türk'
        "maarif": [], # Matches 'maarıf'
        "truncated": [], # Ends in 'lk', 'tk' etc.
        "generic_ı": [] # Any 'ı' where 'i' common
    }
    
    for item in data["dosyalar"]:
        name = item["ders"]
        lower_name = name.lower()
        
        if "ı" in lower_name:
            if any(x in lower_name for x in ["dılı", "bılgısı", "ıletısım", "muzık", "matematık", "ingılızce"]):
                issues["tı_bı_dı"].append(name)
            else:
                issues["generic_ı"].append(name)
        
        if "turk" in lower_name and "türk" not in lower_name:
            issues["turk_u"].append(name)
            
        if "maarıf" in lower_name:
            issues["maarif"].append(name)
            
        if re.search(r'[a-z]{2,}[bcdfghjklmnpqrstvwxyz]$', lower_name) and not lower_name.endswith("lük") and not lower_name.endswith("lik"):
             # Simple check for words ending in consonants that might be truncated (e.g. Rehberlk, Matematk)
             if any(lower_name.endswith(x) for x in ["lk", "tk", "nk", "js", "gt", "syar"]):
                 issues["truncated"].append(name)

    # Print summary
    for k, v in issues.items():
        unique_v = list(set(v))
        print(f"\n--- {k.upper()} (Unique: {len(unique_v)}) ---")
        for ex in sorted(unique_v)[:20]:
            print(f"  {ex}")

if __name__ == "__main__":
    audit()
