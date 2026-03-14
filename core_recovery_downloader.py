import requests
import os
import time

# Definitive list of IDs to recover
RECOVERY_IDS = [
    # Sınıf Öğretmenliği (Primary 2-4)
    1842, 226, 233, 243, 1621, 1698, 1670, 1950, # Grade 2
    227, 234, 244, 253, 1512, 1517, 1720, 1727, 1730, 1738, 1739, 1904, 1905, 1906, 2026, # Grade 3
    228, 235, 242, 245, 246, 254, 1509, 1516, 1721, 1728, 1731, 1740, 1741, # Grade 4
    
    # İngilizce
    1943, 240, 241, 1939, 1940, 1982, 1283, 1454, 1941, 167, 1284, 1942, 168, 1285, 
    1700, 1702, 1945, 1983, 1279, 1453, 1703, 1707, 67, 1274, 1704, 1708, 68, 1275, 1705, 1709,
    
    # Din Kültürü
    1755, 231, 1773, 1131, 1754, 1781, 1756, 1774, 1782, 153, 178, 1757, 1779, 154, 179, 
    1758, 1780, 1786, 1759, 1775, 2016, 2021, 1760, 1776, 1995, 1761, 71, 100, 1777, 72, 73, 101, 1762, 1778,
    
    # Fen Bilimleri
    1605, 1550, 1606, 1551, 1722, 1723,
    
    # Sosyal Bilgiler
    804, 1227, 1647, 2017, 1222, 1272, 1286, 1648, 1862, 1228, 1229, 1225, 1287, 1732, 1861, 1158, 1230, 1233, 1226, 1288
]

# Remove duplicates
RECOVERY_IDS = list(set(RECOVERY_IDS))

os.makedirs("word_planlar", exist_ok=True)

print(f"Starting recovery for {len(RECOVERY_IDS)} items...")

success_count = 0
for i in RECOVERY_IDS:
    url = f"https://defterdoldur.com/planword/{i}"
    filename = f"word_planlar/downloaded_{i}.docx"
    
    # Skip if already exists
    if os.path.exists(filename):
        print(f"[{i}] Skipping, already exists.")
        continue
        
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"[{i}] Saved.")
            success_count += 1
        else:
            print(f"[{i}] Failed: {r.status_code}")
    except Exception as e:
        print(f"[{i}] Error: {e}")
    
    # Small delay to be polite
    time.sleep(1)

print(f"\nRecovery Job Done. {success_count} new files downloaded.")
