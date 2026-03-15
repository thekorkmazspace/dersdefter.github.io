#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.common.paths import PUBLIC_DIR


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    index_path = PUBLIC_DIR / "index.json"
    catalog_path = PUBLIC_DIR / "meta" / "catalog.json"

    if not index_path.exists():
        print("Eksik dosya: public/index.json")
        return 1
    if not catalog_path.exists():
        print("Eksik dosya: public/meta/catalog.json")
        return 1

    index_payload = load_json(index_path)
    catalog_payload = load_json(catalog_path)
    entries = index_payload.get("dosyalar", [])

    missing_files = []
    row_mismatches = []
    ids = []

    for entry in entries:
        plan_path = PUBLIC_DIR / entry["dosya"]
        ids.append(entry["id"])
        if not plan_path.exists():
            missing_files.append(entry["dosya"])
            continue
        plan_payload = load_json(plan_path)
        row_count = len(plan_payload.get("plan", []))
        if row_count != entry["kayit_sayisi"]:
            row_mismatches.append((entry["id"], entry["kayit_sayisi"], row_count))

    duplicate_ids = [plan_id for plan_id, count in Counter(ids).items() if count > 1]
    suspect_count = len(catalog_payload.get("suspect_names", []))

    if missing_files:
        print("Eksik yayın dosyaları:")
        for path in missing_files[:20]:
            print(path)
        return 1

    if duplicate_ids:
        print("Tekrarlı plan ID bulundu:", duplicate_ids[:20])
        return 1

    if row_mismatches:
        print("Kayıt sayısı uyumsuzlukları:")
        for item in row_mismatches[:20]:
            print(item)
        return 1

    print(f"Toplam plan: {len(entries)}")
    print(f"Şüpheli ad sayısı: {suspect_count}")
    print("Yayın doğrulaması geçti.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
