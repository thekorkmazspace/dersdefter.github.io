import requests
import os
import time

# Klasör oluşturma
output_dir = "word_planlar"
os.makedirs(output_dir, exist_ok=True)

print(f"İşlem başlıyor. Dosyalar '{output_dir}' klasörüne kaydedilecek.\n")

for i in range(100, 1001):
    url = f"https://defterdoldur.com/planword/{i}"
    filename = os.path.join(output_dir, f"plan_{i}.docx")
    
    # Eğer dosya zaten varsa indirme (resume desteği gibi)
    if os.path.exists(filename):
        print(f"[{i}] Zaten mevcut, atlanıyor.")
        continue

    try:
        print(f"[{i}] İndiriliyor: {url}")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            # İçeriğin gerçekten bir zip/docx dosyası olup olmadığını basitçe kontrol edebiliriz 
            # (PK ile başlar)
            if response.content.startswith(b'PK'):
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"[{i}] Başarıyla kaydedildi.")
            else:
                print(f"[{i}] Hata: Geçersiz dosya formatı (Word değil).")
        elif response.status_code == 404:
            print(f"[{i}] Bulunamadı (404).")
        else:
            print(f"[{i}] HTTP Hatası: {response.status_code}")
            
    except Exception as e:
        print(f"[{i}] Bağlantı hatası: {e}")
        time.sleep(5) # Hata durumunda biraz daha uzun bekle
        
    # Sunucuyu yormamak ve banlanmamak için kısa bekleme
    time.sleep(0.5)

print("\nBütün tarama tamamlandı.")
