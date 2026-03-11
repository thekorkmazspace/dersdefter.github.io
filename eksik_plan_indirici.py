import requests, docx, json, time, os
from io import BytesIO
import google.generativeai as genai
from google.api_core import exceptions

# GEMINI API KEY (Kullanıcının mevcut scriptinden alındı)
API_KEY = "AIzaSyBVSrIt_g1nrELRt1Iu1J1GOQp02PhA-aI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Hedef klasörler
JSON_DIR = "json_planlar"
os.makedirs(JSON_DIR, exist_ok=True)

# Tespit edilen eksik plan ID'leri ve açıklamaları
eksik_planlar = [
    {"id": 1662, "ders": "Edebiyat", "sinif": 10},
    {"id": 1625, "ders": "Matematik", "sinif": 10},
    {"id": 1691, "ders": "Fizik", "sinif": 10},
    {"id": 1735, "ders": "Biyoloji", "sinif": 10},
    {"id": 1650, "ders": "Tarih", "sinif": 10},
    {"id": 1709, "ders": "Coğrafya", "sinif": 10},
    {"id": 1699, "ders": "İngilizce", "sinif": 10},
    {"id": 1760, "ders": "Din Kültürü", "sinif": 10},
    {"id": 1754, "ders": "Din Kültürü", "sinif": 5},
    {"id": 1756, "ders": "Din Kültürü", "sinif": 6},
    {"id": 1757, "ders": "Din Kültürü", "sinif": 7},
    {"id": 1758, "ders": "Din Kültürü", "sinif": 8},
    {"id": 1759, "ders": "Din Kültürü", "sinif": 9},
    {"id": 1761, "ders": "Din Kültürü", "sinif": 11},
    {"id": 1762, "ders": "Din Kültürü", "sinif": 12},
    {"id": 1842, "ders": "Müzik", "sinif": 2},
    {"id": 1864, "ders": "Müzik", "sinif": 6},
    {"id": 1865, "ders": "Müzik", "sinif": 7},
    {"id": 1866, "ders": "Müzik", "sinif": 8},
    {"id": 149, "ders": "Beden Eğitimi", "sinif": 7},
    {"id": 150, "ders": "Beden Eğitimi", "sinif": 8}
]

def clean_json_text(text):
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def process_plan(plan_info):
    plan_id = plan_info["id"]
    url = f"https://defterdoldur.com/planword/{plan_id}"
    print(f"[{plan_id}] İşleniyor: {plan_info['ders']} - {plan_info['sinif']}. Sınıf")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"[{plan_id}] HTTP Hatası: {response.status_code}")
            return False
            
        doc = docx.Document(BytesIO(response.content))
        tam_metin = "\n".join([para.text for para in doc.paragraphs])
        
        prompt = f"""
        Aşağıdaki metin bir öğretmenin yıllık ders planıdır. Lütfen metni analiz et ve SADECE aşağıdaki JSON formatında çıktı ver.
        'ders' alanını küçük harflerle, Türkçe karakter kullanmadan ve boşluk yerine alt tire ile yaz (örn: fen_bilimleri, ingilizce, hayat_bilgisi).
        'sinif' alanı sadece rakam olmalı.
        {{
          "sinif": {plan_info['sinif']},
          "ders": "{plan_info['ders'].lower()}",
          "plan": [ {{"hafta": 1, "tarih": "Eylül 1-5", "kazanim": "...", "kod": "..."}} ]
        }}
        Metin: {tam_metin[:10000]}
        """
        
        while True:
            try:
                ai_yanit = model.generate_content(prompt)
                break
            except exceptions.ResourceExhausted:
                print(f"[{plan_id}] Kota doldu. 60sn bekleniyor...")
                time.sleep(60)
            except Exception as e:
                print(f"[{plan_id}] AI Hatası: {e}")
                return False

        json_metni = clean_json_text(ai_yanit.text)
        try:
            veri = json.loads(json_metni)
        except json.JSONDecodeError:
            print(f"[{plan_id}] JSON Parse Hatası!")
            return False
            
        # Dosya adını sanitize et
        safe_ders = veri.get('ders', 'unknown').replace(" ", "_").lower()
        dosya_adi = f"grade_{veri.get('sinif', 'unknown')}_{safe_ders}_{plan_id}.json"
        dosya_yolu = os.path.join(JSON_DIR, dosya_adi)
        
        with open(dosya_yolu, "w", encoding="utf-8") as f:
            # Mevcut yapıya uygun olarak sadece 'plan' listesini değil, tüm objeyi kaydediyoruz (veya sadece plan listesi miydi?)
            # plan_indirici.py: json.dump(veri.get('plan', []), f, ...) -> sadece listeyi kaydediyordu.
            # Ama index.json 'ders' ve 'sinif' bilgilerini de bu dosyalardan mı alıyor? 
            # jsoner.py incelendiğinde dosyaların içinde 'sinif' ve 'ders' kökleri de var.
            json.dump(veri, f, ensure_ascii=False, indent=2)
            
        print(f"[{plan_id}] Başarıyla kaydedildi: {dosya_adi}")
        return True

    except Exception as e:
        print(f"[{plan_id}] Genel Hata: {e}")
        return False

# Main Execution
success_count = 0
for plan in eksik_planlar:
    if process_plan(plan):
        success_count += 1
    time.sleep(10) # API ve Server limitleri için

print(f"\nİşlem Tamamlandı. {success_count}/{len(eksik_planlar)} plan eklendi.")
