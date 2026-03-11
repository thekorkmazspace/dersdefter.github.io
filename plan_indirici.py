import requests, docx, json, time, os
from io import BytesIO
import google.generativeai as genai
from google.api_core import exceptions

# Gemini API ayarları
genai.configure(api_key="AIzaSyBVSrIt_g1nrELRt1Iu1J1GOQp02PhA-aI")
model = genai.GenerativeModel('gemini-2.0-flash') # En güncel Flash modeli

os.makedirs("json_planlar", exist_ok=True)

for i in range(100, 1000):
    url = f"https://defterdoldur.com/planword/{i}"
    print(f"[{i}] İndiriliyor: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            try:
                # Word dosyasını hafızada okuma
                doc = docx.Document(BytesIO(response.content))
            except Exception as e:
                print(f"[{i}] Dosya okuma hatası (Bozuk dosya olabilir): {e}")
                continue
                
            tam_metin = "\n".join([para.text for para in doc.paragraphs])
            
            # Sınıf ve ders adını JSON'un ana kökünde isteyen güncel prompt
            prompt = f"""
            Aşağıdaki metin bir öğretmenin yıllık ders planıdır. Lütfen metni analiz et ve SADECE aşağıdaki JSON formatında çıktı ver.
            'ders' alanını küçük harflerle, Türkçe karakter kullanmadan ve boşluk yerine alt tire ile yaz (örn: fen_bilimleri, ingilizce, hayat_bilgisi).
            {{
              "sinif": 7,
              "ders": "ingilizce",
              "plan": [ {{"hafta": 1, "tarih": "Eylül 1-5", "kazanim": "...", "kod": "..."}} ]
            }}
            Metin: {tam_metin[:8000]}
            """
            
            while True:
                try:
                    ai_yanit = model.generate_content(prompt)
                    break
                except exceptions.ResourceExhausted:
                    print(f"[{i}] Kota doldu (429). 60 saniye bekleniyor...")
                    time.sleep(60)
                except Exception as e:
                    print(f"[{i}] AI Yanıt hatası: {e}")
                    raise e

            json_metni = ai_yanit.text.replace("```json", "").replace("```", "").strip()
            
            # JSON metnini okuyup dinamik dosya adı oluşturma
            veri = json.loads(json_metni)
            dosya_adi = f"grade_{veri.get('sinif', 'unknown')}_{veri.get('ders', 'unknown')}.json"
            dosya_yolu = os.path.join("json_planlar", dosya_adi)
            
            with open(dosya_yolu, "w", encoding="utf-8") as f:
                json.dump(veri.get('plan', []), f, ensure_ascii=False, indent=2)
                
            print(f"[{i}] Başarıyla kaydedildi: {dosya_adi}")
            
        else:
            print(f"[{i}] Bulunamadı (HTTP {response.status_code})")
    except Exception as e:
        print(f"[{i}] Genel hata oluştu: {e}")
    
    # Ücretsiz katman limitlerine takılmamak için daha uzun bekleme
    time.sleep(5)