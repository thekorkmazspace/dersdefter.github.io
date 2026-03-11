import os, docx, json, requests, re, time

word_dir = "word_planlar"
dosyalar = sorted([f for f in os.listdir(word_dir) if f.endswith(".docx")])[:3]

print(f"Hız testi başlıyor (3 dosya denenecek)...")
baslangic_toplam = time.time()

for dosya_adi in dosyalar:
    baslangic_dosya = time.time()
    try:
        doc = docx.Document(os.path.join(word_dir, dosya_adi))
        metin_parcalari = [p.text for p in doc.paragraphs]
        for tablo in doc.tables:
            for satir in tablo.rows:
                hucre_metinleri = [hucre.text.strip() for hucre in satir.cells]
                metin_parcalari.append(" | ".join(hucre_metinleri))
        
        tam_metin = "\n".join(metin_parcalari)[:4000]
        
        print(f"[{dosya_adi}] Ollama işliyor...")
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": f"Yıllık planı analiz et ve sadece JSON ver: {tam_metin}",
            "stream": False
        }, timeout=300)
        
        sure = time.time() - baslangic_dosya
        print(f"[{dosya_adi}] Tamamlandı: {sure:.2f} saniye.")
    except Exception as e:
        print(f"[{dosya_adi}] Hata: {e}")

toplam_sure = time.time() - baslangic_toplam
print(f"\n3 dosya için ortalama süre: {toplam_sure/3:.2f} saniye.")
