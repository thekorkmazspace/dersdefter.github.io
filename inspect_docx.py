#!/usr/bin/env python3
import requests, docx
from io import BytesIO

url = 'https://defterdoldur.com/planword/1949'
r = requests.get(url, timeout=15)
print('Status:', r.status_code)
doc = docx.Document(BytesIO(r.content))
print('Paragraf sayisi:', len(doc.paragraphs))
print('Tablo sayisi:', len(doc.tables))
print()
print('=== ILK 15 PARAGRAF ===')
for i, p in enumerate(doc.paragraphs[:15]):
    print(f'P{i}: [{p.text.strip()}]')
print()
if doc.tables:
    print('=== TABLO 0 - ILK 8 SATIR ===')
    t = doc.tables[0]
    print('Sutun sayisi:', len(t.columns))
    for i, row in enumerate(t.rows[:8]):
        cells = [c.text.strip() for c in row.cells]
        print(f'R{i}: {cells}')
    print()
    print('=== TABLO 0 - SATIR 8-15 ===')
    for i, row in enumerate(t.rows[8:15], start=8):
        cells = [c.text.strip() for c in row.cells]
        print(f'R{i}: {cells}')
