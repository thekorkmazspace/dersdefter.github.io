#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.common.paths import DATA_DIR, PUBLIC_DIR, PUBLIC_META_DIR, PUBLIC_PLANS_DIR


SOURCE_INDEX = DATA_DIR / "index.json"
SOURCE_NAMES = DATA_DIR / "official_names.json"
PLAN_ID_RE = re.compile(r"_(\d+)\.json$")

DISPLAY_FIXES = {
    "Secmeli": "Seçmeli",
    "Dıkkate": "Dikkate",
    "Gerekır": "Gerekir",
    "Ogretım": "Öğretim",
    "Surecınde": "Sürecinde",
    "Farklılıgı": "Farklılığı",
    "Edebiyati": "Edebiyatı",
    "Saglıklı": "Sağlıklı",
    "Becerilerı": "Becerileri",
    "Dilı": "Dili",
}

ROMAN_FIXES = (
    ("I-II-IIIi", "I-II-III"),
    ("I-II-IIIıi", "I-II-III"),
)

SUSPECT_PATTERNS = (
    r"&#\d+;",
    r"I-II-III[iı]",
    r"\bSecmeli\b",
    r"\bDıkkate\b",
    r"\bOgretım\b",
    r"\bSurecınde\b",
)

ENG_THEME_CODE_RE = re.compile(r"\bENG\.(?:PREP|\d+)\.(\d+)\.")
ENG_THEME_LABEL_RE = re.compile(r"\bTHEME\s+(\d+)\b", re.IGNORECASE)
NUMERIC_THEME_LABEL_RE = re.compile(r"(?<!\d)(\d{1,2})\.\s*")
SPECIAL_WEEK_PREFIXES = (
    "FIRST MIDTERM BREAK",
    "SECOND MIDTERM BREAK",
    "1ST MIDTERM BREAK",
    "2ND MIDTERM BREAK",
    "MIDTERM BREAK",
    "1ST MIDTERM HOLIDAY",
    "2ND MIDTERM HOLIDAY",
    "MIDTERM HOLIDAY",
    "HOLIDAY",
    "YARIYIL TATILI",
    "YARIYIL TATİLİ",
    "ARA TATILI",
    "ARA TATİLİ",
    "EID AL-",
    "OKUL TEMELLI",
    "OKUL TEMELLİ",
    "SINAV",
    "EXAM",
)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dedupe_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def extract_theme_codes(text: str) -> list[str]:
    return dedupe_preserving_order(ENG_THEME_CODE_RE.findall(text or ""))


def extract_theme_numbers_from_unit(text: str) -> list[str]:
    source = text or ""
    if "THEME" in source.upper():
        matches = ENG_THEME_LABEL_RE.findall(source)
    else:
        matches = NUMERIC_THEME_LABEL_RE.findall(source)
    return dedupe_preserving_order(matches)


def starts_with_special_prefix(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.upper()).strip()
    return any(normalized.startswith(prefix) for prefix in SPECIAL_WEEK_PREFIXES)


def is_special_week(row: dict) -> bool:
    return any(
        starts_with_special_prefix(str(row.get(key, "")))
        for key in ("ÜNİTE", "KONU", "KAZANIM")
    )


def get_row_theme(row: dict) -> str | None:
    theme_codes = extract_theme_codes(str(row.get("KAZANIM", "")))
    if theme_codes:
        return theme_codes[0]

    unit_themes = extract_theme_numbers_from_unit(str(row.get("ÜNİTE", "")))
    if unit_themes:
        return unit_themes[0]

    return None


def is_mixed_english_theme_row(row: dict) -> bool:
    unit_text = str(row.get("ÜNİTE", ""))
    if "REVISION" in unit_text.upper():
        return False

    theme_codes = extract_theme_codes(str(row.get("KAZANIM", "")))
    unit_themes = extract_theme_numbers_from_unit(unit_text)
    return len(theme_codes) > 1 or len(unit_themes) > 1


def trim_kazanim_to_primary_theme(text: str, primary_theme: str | None) -> str:
    if not text or not primary_theme:
        return text

    matches = list(ENG_THEME_CODE_RE.finditer(text))
    if len(matches) < 2:
        return text

    owner_seen = False
    for match in matches:
        theme_number = match.group(1)
        if theme_number == primary_theme:
            owner_seen = True
            continue
        if owner_seen:
            return text[: match.start()].rstrip(" |\n")
    return text


def trim_topic_to_primary_theme(text: str) -> str:
    if not text or text.count("Sub-themes") < 2:
        return text

    first_marker = text.find("Sub-themes")
    second_marker = text.find("Sub-themes", first_marker + len("Sub-themes"))
    if second_marker == -1:
        return text
    return text[:second_marker].rstrip(" |\n")


def normalize_english_theme_rows(rows: list[dict]) -> list[dict]:
    normalized_rows = [dict(row) for row in rows]
    row_themes = [get_row_theme(row) for row in rows]
    mixed_rows = [is_mixed_english_theme_row(row) for row in rows]

    for current_index, row in enumerate(rows):
        row_theme = row_themes[current_index]
        if not row_theme or not mixed_rows[current_index]:
            continue

        candidate_indices = []
        for candidate_index, candidate in enumerate(rows):
            if candidate_index == current_index:
                continue
            if row_themes[candidate_index] != row_theme:
                continue
            if mixed_rows[candidate_index]:
                continue
            if is_special_week(candidate):
                continue
            candidate_indices.append(candidate_index)

        if not candidate_indices:
            template_row = None
        else:
            template_index = min(
                candidate_indices,
                key=lambda candidate_index: (
                    abs(candidate_index - current_index),
                    0 if candidate_index < current_index else 1,
                ),
            )
            template_row = rows[template_index]

        if template_row is not None:
            for key in ("ÜNİTE", "KONU", "KAZANIM"):
                value = template_row.get(key)
                if value:
                    normalized_rows[current_index][key] = value

        normalized_rows[current_index]["KONU"] = trim_topic_to_primary_theme(
            str(normalized_rows[current_index].get("KONU", ""))
        )
        normalized_rows[current_index]["KAZANIM"] = trim_kazanim_to_primary_theme(
            str(normalized_rows[current_index].get("KAZANIM", "")),
            row_theme,
        )

    return normalized_rows


def sanitize_plan_payload(plan_payload: dict) -> dict:
    normalized_rows = normalize_english_theme_rows(plan_payload.get("plan", []))
    sanitized_rows = []
    for row in normalized_rows:
        sanitized_row = {
            key: value
            for key, value in row.items()
            if key not in {"ÜNİTE", "SDB", "OB"}
        }
        sanitized_rows.append(sanitized_row)

    sanitized_payload = dict(plan_payload)
    sanitized_payload["plan"] = sanitized_rows
    return sanitized_payload


def extract_plan_id(filename: str) -> int:
    match = PLAN_ID_RE.search(filename)
    if not match:
        raise ValueError(f"Plan ID ayıklanamadı: {filename}")
    return int(match.group(1))


def normalize_display_name(name: str) -> str:
    cleaned = html.unescape(name).strip()
    for old, new in DISPLAY_FIXES.items():
        cleaned = cleaned.replace(old, new)
    for old, new in ROMAN_FIXES:
        cleaned = cleaned.replace(old, new)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def detect_suspect_names(entries: list[dict]) -> list[dict]:
    suspects = []
    patterns = [re.compile(pattern) for pattern in SUSPECT_PATTERNS]
    for entry in entries:
        if any(pattern.search(entry["ders"]) for pattern in patterns):
            suspects.append(
                {
                    "id": entry["id"],
                    "dosya": entry["dosya"],
                    "ders": entry["ders"],
                }
            )
    return suspects


def reset_public_dir() -> None:
    if PUBLIC_PLANS_DIR.exists():
        shutil.rmtree(PUBLIC_PLANS_DIR)
    PUBLIC_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_META_DIR.mkdir(parents=True, exist_ok=True)


def build_public() -> None:
    source_index = load_json(SOURCE_INDEX)
    official_names = load_json(SOURCE_NAMES) if SOURCE_NAMES.exists() else {}

    reset_public_dir()

    public_entries = []
    legacy_mappings = []
    total_rows = 0

    for source_entry in source_index["dosyalar"]:
        legacy_name = source_entry["dosya"]
        source_plan_path = DATA_DIR / legacy_name
        if not source_plan_path.exists():
            raise FileNotFoundError(f"Eksik plan dosyası: {source_plan_path}")

        plan_id = extract_plan_id(legacy_name)
        public_plan_name = f"{plan_id}.json"
        public_plan_path = PUBLIC_PLANS_DIR / public_plan_name

        plan_payload = sanitize_plan_payload(load_json(source_plan_path))
        normalized_name = normalize_display_name(
            official_names.get(str(plan_id), source_entry["ders"])
        )
        plan_payload["ders"] = normalized_name

        with public_plan_path.open("w", encoding="utf-8") as handle:
            json.dump(plan_payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

        total_rows += len(plan_payload.get("plan", []))
        public_entries.append(
            {
                "id": plan_id,
                "sinif": source_entry["sinif"],
                "ders": normalized_name,
                "kayit_sayisi": source_entry["kayit_sayisi"],
                "dosya": f"plans/{public_plan_name}",
            }
        )
        legacy_mappings.append(
            {
                "id": plan_id,
                "legacy_dosya": legacy_name,
                "public_dosya": f"plans/{public_plan_name}",
            }
        )

    public_entries.sort(key=lambda item: (-1 if item["sinif"] == "Hazırlık" else int(item["sinif"]), item["ders"], item["id"]))

    grade_counts = Counter(item["sinif"] for item in public_entries)
    duplicate_counts = Counter(item["ders"] for item in public_entries)
    duplicates = [
        {"ders": lesson_name, "adet": count}
        for lesson_name, count in duplicate_counts.items()
        if count > 1
    ]
    duplicates.sort(key=lambda item: (-item["adet"], item["ders"]))

    public_index = {
        "surum": 1,
        "uretildi_at": datetime.now(timezone.utc).isoformat(),
        "toplam": len(public_entries),
        "dosyalar": public_entries,
    }
    catalog = {
        "total_plans": len(public_entries),
        "total_rows": total_rows,
        "grade_counts": dict(sorted(grade_counts.items(), key=lambda item: str(item[0]))),
        "duplicate_lessons": duplicates,
        "suspect_names": detect_suspect_names(public_entries),
        "legacy_mappings": legacy_mappings,
    }

    with (PUBLIC_DIR / "index.json").open("w", encoding="utf-8") as handle:
        json.dump(public_index, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with (PUBLIC_META_DIR / "catalog.json").open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    build_public()
