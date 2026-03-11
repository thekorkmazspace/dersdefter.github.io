import os, docx, json, requests, re, time

os.makedirs("json_planlar", exist_ok=True)

# Mevcut dosyaları listele (Atlamak için)
mevcut_jsonlar = os.listdir("json_planlar")

for dosya_adi in sorted(os.listdir("word_planlar")):
    if dosya_adi.endswith(".docx"):
        try:
            doc = docx.Document(os.path.join("word_planlar", dosya_adi))
            
            # Paragraflardan metin çekme
            metin_parcalari = [p.text for p in doc.paragraphs]
            
            # Tablolardan metin çekme
            for tablo in doc.tables:
                for satir in tablo.rows:
                    hucre_metinleri = [hucre.text.strip() for hucre in satir.cells]
                    metin_parcalari.append(" | ".join(hucre_metinleri))
            
            tam_metin = "\n".join(metin_parcalari)
            if not tam_metin.strip() or len(tam_metin) < 100: 
                continue
            
            # Dosya adını önceden belirle ki zaten varsa atlayabilelim
            # Not: sinif/ders AI'dan geldiği için başta bilmiyoruz ama plan_{i}.json gibi 
            # bir eşleme yapabiliriz veya çıktı adını tahmin edebiliriz.
            # Şimdilik her dosyayı işleyelim ama hata yönetimini güçlendirelim.
            
            print(f"İşleniyor: {dosya_adi}")
            
            prompt = f"""Aşağıdaki metin bir öğretmenin yıllık ders planıdır. Lütfen metni analiz et ve SADECE aşağıdaki JSON formatında çıktı ver.
            'ders' alanını küçük harflerle, Türkçe karakter kullanmadan ve boşluk yerine alt tire ile yaz.
            {{
              "sinif": 7,
              "ders": "ingilizce",
              "plan": [ {{"hafta": 1, "tarih": "Eylül 1-5", "kazanim": "...", "kod": "..."}} ]
            }}
            Metin: {tam_metin[:4000]}"""
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post("http://localhost:11434/api/generate", json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }, timeout=300) # Timeout 5 dakikaya çıkarıldı
                    
                    if response.status_code == 200:
                        raw_response = response.json().get("response", "")
                        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                        if json_match:
                            json_metni = json_match.group(0)
                            veri = json.loads(json_metni)
                            
                            output_filename = f"json_planlar/grade_{veri.get('sinif', 'unknown')}_{veri.get('ders', 'unknown')}.json"
                            
                            with open(output_filename, "w", encoding="utf-8") as f:
                                json.dump(veri.get('plan', []), f, ensure_ascii=False, indent=2)
                            print(f"Kaydedildi: {output_filename}")
                            break # Başarılı, döngüden çık
                        else:
                            print(f"Hata: JSON formatı bulunamadı ({dosya_adi})")
                            break
                    else:
                        print(f"Hata: HTTP {response.status_code} ({dosya_adi})")
                        break
                        
                except requests.exceptions.Timeout:
                    print(f"[{attempt+1}/{max_retries}] Zaman aşımı! Tekrar deneniyor... ({dosya_adi})")
                    time.sleep(10) # 10 saniye bekle ve tekrar dene
                except Exception as e:
                    print(f"Hata ({dosya_adi}): {e}")
                    break
            
        except Exception as e:
            print(f"Hata ({dosya_adi}): {e}")
