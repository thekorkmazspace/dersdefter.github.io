import requests
import os
import time

# Klasör oluşturma
output_dir = "word_planlar"
os.makedirs(output_dir, exist_ok=True)

# Tespit edilen eksik plan ID'leri
eksik_ids = [
    1662, 1625, 1691, 1735, 1650, 1709, 1699, 1760, # 10. Sınıf
    1754, 1756, 1757, 1758, 1759, 1761, 1762,       # Din Kültürü
    1842, 1864, 1865, 1866,                         # Müzik
    149, 150                                        # Beden Eğitimi
]

print(f"İşlem başlıyor. {len(eksik_ids)} adet dosya '{output_dir}' klasörüne kaydedilecek.\n")

success_count = 0
for i in eksik_ids:
    url = f"https://defterdoldur.com/planword/{i}"
    filename = os.path.join(output_dir, f"plan_{i}.docx")
    
    if os.path.exists(filename):
        print(f"[{i}] Zaten mevcut, atlanıyor.")
        success_count += 1
        continue

    try:
        print(f"[{i}] İndiriliyor: {url}")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            if response.content.startswith(b'PK'):
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"[{i}] Başarıyla kaydedildi.")
                success_count += 1
            else:
                print(f"[{i}] Hata: Geçersiz dosya formatı (Word değil).")
        else:
            print(f"[{i}] HTTP Hatası: {response.status_code}")
            
    except Exception as e:
        print(f"[{i}] Bağlantı hatası: {e}")
        
    time.sleep(0.5)

print(f"\nİşlem tamamlandı. {success_count}/{len(eksik_ids)} dosya hazır.")
