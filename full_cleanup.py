#!/usr/bin/env python3
"""
Comprehensive cleanup script for lesson plan data.
1. Cleans data/json_planlar/ by removing duplicate files, keeping only canonical versions
2. Rebuilds data/json_planlar/index.json from data/index.json
3. Copies canonical files from data/ to data/json_planlar/
4. Fixes lesson names in sinif_rehberlik_json/
5. Audits kazanım fields, dates, weeks
"""
import json, os, re, shutil, glob
from pathlib import Path
from collections import defaultdict

BASE = Path("/home/fatih/Masaüstü/Yıllık Planlar")
DATA_DIR = BASE / "data"
JP_DIR = DATA_DIR / "json_planlar"
REHBERLIK_DIR = BASE / "sinif_rehberlik_json"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path.name}")

# ============================================================
# STEP 1: Clean data/json_planlar/ - remove ALL json files
# ============================================================
print("=" * 60)
print("STEP 1: Cleaning data/json_planlar/")
print("=" * 60)

# Count existing files
existing_jp = list(JP_DIR.glob("grade_*.json"))
print(f"  Found {len(existing_jp)} JSON files in data/json_planlar/")

# Remove all grade_*.json files
removed = 0
for f in existing_jp:
    f.unlink()
    removed += 1
print(f"  Removed {removed} files")

# Also remove the old index.json
old_idx = JP_DIR / "index.json"
if old_idx.exists():
    old_idx.unlink()
    print("  Removed old index.json")

# ============================================================
# STEP 2: Copy canonical files from data/ to data/json_planlar/
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Copying canonical files from data/ to data/json_planlar/")
print("=" * 60)

# Load the data/index.json (source of truth)
data_index = load_json(DATA_DIR / "index.json")
print(f"  data/index.json has {data_index['toplam']} entries")

copied = 0
missing = []
for entry in data_index['dosyalar']:
    src = DATA_DIR / entry['dosya']
    dst = JP_DIR / entry['dosya']
    if src.exists():
        shutil.copy2(src, dst)
        copied += 1
    else:
        missing.append(entry['dosya'])
        print(f"  WARNING: Missing source file: {entry['dosya']}")

print(f"  Copied {copied} files")
if missing:
    print(f"  Missing {len(missing)} files!")

# Copy data/index.json to data/json_planlar/index.json
shutil.copy2(DATA_DIR / "index.json", JP_DIR / "index.json")
print("  Copied index.json")

# Keep belirli_gun_ve_haftalar.json if exists
bgvh = JP_DIR / "belirli_gun_ve_haftalar.json"
if not bgvh.exists():
    # Check if data has it
    src_bgvh = DATA_DIR / "belirli_gun_ve_haftalar.json"
    if src_bgvh.exists():
        shutil.copy2(src_bgvh, bgvh)
        print("  Copied belirli_gun_ve_haftalar.json")

# ============================================================
# STEP 3: Audit kazanım fields in data/ files
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Auditing kazanım/öğrenim çıktısı fields")
print("=" * 60)

empty_kazanim_files = []
kazanim_keys = ["KAZANIM", "KAZANIMLAR", "ÖĞRENİM ÇIKTISI", "ÖĞRENME ÇIKTILARI VE SÜREÇ BİLEŞENLERİ", "KONULAR VE KAZANIMLAR"]
# Also check for common variations
all_kazanim_like = re.compile(r'kazanım|kazanim|öğrenim|öğrenme|çıktı', re.IGNORECASE)

total_checked = 0
total_empty_entries = 0
files_with_issues = []

for entry in data_index['dosyalar']:
    fpath = DATA_DIR / entry['dosya']
    if not fpath.exists():
        continue
    
    try:
        data = load_json(fpath)
    except:
        print(f"  ERROR reading: {entry['dosya']}")
        continue
    
    total_checked += 1
    plan = data.get('plan', [])
    empty_count = 0
    
    for i, week in enumerate(plan):
        # Find the kazanım field (could be named differently)
        kazanim_val = None
        kazanim_key = None
        for k, v in week.items():
            if k in kazanim_keys or all_kazanim_like.search(k):
                kazanim_val = v
                kazanim_key = k
                break
        
        if kazanim_val is None:
            # No kazanım field found at all - check if it's a holiday week
            unite = week.get('ÜNİTE', '') or week.get('UNITE', '') or ''
            if any(x in unite.lower() for x in ['tatil', 'etkinlik']):
                continue
            empty_count += 1
        elif isinstance(kazanim_val, str) and kazanim_val.strip() == '':
            # Empty string
            unite = week.get('ÜNİTE', '') or week.get('UNITE', '') or ''
            if any(x in unite.lower() for x in ['tatil', 'etkinlik']):
                continue
            empty_count += 1
    
    if empty_count > 0:
        total_empty_entries += empty_count
        files_with_issues.append((entry['dosya'], entry['ders'], empty_count, len(plan)))

print(f"  Checked {total_checked} files")
print(f"  Files with empty kazanım entries: {len(files_with_issues)}")
print(f"  Total empty kazanım entries: {total_empty_entries}")

if files_with_issues:
    print("\n  Top 20 files with most issues:")
    files_with_issues.sort(key=lambda x: x[2], reverse=True)
    for fname, ders, empty_c, total_c in files_with_issues[:20]:
        print(f"    {fname}: {empty_c}/{total_c} empty - {ders}")

# ============================================================
# STEP 4: Check dates and weeks consistency  
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: Checking dates and weeks consistency")
print("=" * 60)

date_issues = []
for entry in data_index['dosyalar']:
    fpath = DATA_DIR / entry['dosya']
    if not fpath.exists():
        continue
    
    try:
        data = load_json(fpath)
    except:
        continue
    
    plan = data.get('plan', [])
    weeks_seen = set()
    
    for i, week in enumerate(plan):
        hafta = week.get('HAFTA', '')
        if hafta:
            # Extract week number
            match = re.match(r'(\d+)', hafta)
            if match:
                wnum = int(match.group(1))
                if wnum in weeks_seen:
                    date_issues.append((entry['dosya'], f"Duplicate week {wnum}"))
                weeks_seen.add(wnum)

print(f"  Files with duplicate week numbers: {len(date_issues)}")
if date_issues:
    for fname, issue in date_issues[:10]:
        print(f"    {fname}: {issue}")

# ============================================================
# STEP 5: Fix sinif_rehberlik_json typos
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Checking sinif_rehberlik_json/")
print("=" * 60)

rehberlik_files = list(REHBERLIK_DIR.glob("*.json"))
print(f"  Found {len(rehberlik_files)} files")

for rf in rehberlik_files:
    if rf.name == 'sinif_index.json':
        continue
    try:
        data = load_json(rf)
        ders = data.get('ders', '')
        plan = data.get('plan', [])
        empty_k = sum(1 for w in plan if not w.get('KAZANIM', '').strip() 
                       and 'tatil' not in w.get('ÜNİTE', '').lower()
                       and 'etkinlik' not in w.get('ÜNİTE', '').lower())
        print(f"  {rf.name}: ders='{ders}', weeks={len(plan)}, empty_kazanim={empty_k}")
    except Exception as e:
        print(f"  ERROR: {rf.name}: {e}")

# ============================================================
# STEP 6: Final summary
# ============================================================
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

# Count files in data/json_planlar/ now
final_jp = list(JP_DIR.glob("grade_*.json"))
print(f"  data/json_planlar/ now has {len(final_jp)} JSON files (was {len(existing_jp)})")
print(f"  data/index.json entries: {data_index['toplam']}")

# Verify index matches files
jp_index = load_json(JP_DIR / "index.json")
index_files = {e['dosya'] for e in jp_index['dosyalar']}
actual_files = {f.name for f in final_jp}
only_index = index_files - actual_files
only_disk = actual_files - index_files
print(f"  In index but not on disk: {len(only_index)}")
print(f"  On disk but not in index: {len(only_disk)}")

if only_index:
    print("\n  Files in index but missing on disk:")
    for f in sorted(only_index)[:10]:
        print(f"    {f}")

print("\nDone!")
