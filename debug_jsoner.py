import os, docx, json, requests, re

print("Süreç başladı...")
output_dir = "json_planlar"
os.makedirs(output_dir, exist_ok=True)

word_dir = "word_planlar"
dosyalar = sorted(os.listdir(word_dir))
if not dosyalar:
    print("Hata: 'word_planlar' klasörü boş!")
else:
    dosya_adi = dosyalar[0]
    full_path = os.path.join(word_dir, dosya_adi)
    print(f"İlk dosya deneniyor: {full_path}")
    
    try:
        doc = docx.Document(full_path)
        tam_metin = "\n".join([p.text for p in doc.paragraphs])
        print(f"Metin uzunluğu: {len(tam_metin)}")
        
        if len(tam_metin) > 0:
            print("Ollama isteği gönderiliyor...")
            prompt = f"Analiz et: {tam_metin[:1000]}"
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            print("Ollama Durum Kodu:", response.status_code)
            print("Ollama Yanıtı (ilk 100 karakter):", response.text[:100])
        else:
            print("Metin boş, atlanıyor.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

print("Süreç bitti.")
