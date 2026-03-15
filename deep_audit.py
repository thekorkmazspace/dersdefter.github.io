import json
import re

DATA_PATH = "/home/fatih/Masaüstü/Yıllık Planlar/data/index.json"

def audit():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Common Turkish words and their expected forms
    EXPECTED = {
        "egitimi": "Eğitimi", "egitim": "Eğitimi", "ogretim": "Öğretim",
        "turk": "Türk", "kultur": "Kültür", "bilgisayar": "Bilgisayar",
        "ogretmen": "Öğretmen", "gorsel": "Görsel", "muzik": "Müzik",
        "ingilizce": "İngilizce", "matematik": "Matematik", "fizik": "Fizik",
        "biyoloji": "Biyoloji", "kimya": "Kimya", "cografya": "Coğrafya",
        "isaret": "İşaret", "ozel": "Özel", "dili": "Dili", "edebiyati": "Edebiyatı",
        "isletme": "İşletme", "teknolojisi": "Teknolojisi", "teknik": "Teknik",
        "sis": "Sistem", "sistemi": "Sistemi", "bilgisi": "Bilgisi",
        "inkilap": "İnkılap", "ataturkculuk": "Atatürkçülük", "maarif": "Maarif"
    }

    issues = []
    
    for item in data["dosyalar"]:
        name = item["ders"]
        normalized = name.lower().replace('i', 'i').replace('ı', 'i').replace('ü', 'u').replace('ö', 'o').replace('ç', 'c').replace('ş', 's').replace('ğ', 'g')
        
        # Check for non-Turkish characters in words that definitely need them
        # Or check for 'I' vs 'İ' issues
        if "ı" in name.lower() and any(word in name.lower() for word in ["egıtımı", "bılgısı", "dılı", "ıletısım", "muzık", "matematık", "ingılızce"]):
             issues.append({"type": "Dotless I error", "name": name, "file": item["dosya"]})
             
        if any(bad in name.lower() for bad in ["turk ", "gorsel", "muzik", "ozel", "isaret", "cografya"]):
             # These should probably have accents
             issues.append({"type": "Missing Accents", "name": name, "file": item["dosya"]})

        if re.search(r'[a-z]{2,}[bcdfghjklmnpqrstvwxyz]$', name) and not name.lower().endswith(("lük", "lik", "mü", "mi", "mı", "mu")):
            # Possible truncation
            issues.append({"type": "Truncation?", "name": name, "file": item["dosya"]})

    # Group by type and show unique examples
    report = {}
    for issue in issues:
        t = issue["type"]
        if t not in report: report[t] = set()
        report[t].add(issue["name"])

    for t, names in report.items():
        print(f"\n--- {t} ({len(names)}) ---")
        for n in sorted(list(names))[:30]:
            print(f"  {n}")

if __name__ == "__main__":
    audit()
