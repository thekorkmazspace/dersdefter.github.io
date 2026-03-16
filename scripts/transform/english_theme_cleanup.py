from __future__ import annotations

import re


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


def trim_unit_to_primary_theme(text: str, primary_theme: str | None) -> str:
    if not text or not primary_theme:
        return text

    theme_numbers = extract_theme_numbers_from_unit(text)
    if len(theme_numbers) < 2:
        return text

    if "THEME" in text.upper():
        matches = list(ENG_THEME_LABEL_RE.finditer(text))
    else:
        matches = list(NUMERIC_THEME_LABEL_RE.finditer(text))
    if not matches:
        return text

    for index, match in enumerate(matches):
        if match.group(1) != primary_theme:
            continue
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.start() : next_start].strip(" |\n")

    return text


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

        template_row = None
        if candidate_indices:
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

        normalized_rows[current_index]["ÜNİTE"] = trim_unit_to_primary_theme(
            str(normalized_rows[current_index].get("ÜNİTE", "")),
            row_theme,
        )
        normalized_rows[current_index]["KONU"] = trim_topic_to_primary_theme(
            str(normalized_rows[current_index].get("KONU", ""))
        )
        normalized_rows[current_index]["KAZANIM"] = trim_kazanim_to_primary_theme(
            str(normalized_rows[current_index].get("KAZANIM", "")),
            row_theme,
        )

    return normalized_rows


def find_mixed_english_theme_rows(rows: list[dict]) -> list[int]:
    hits = []
    for index, row in enumerate(rows, start=1):
        if is_mixed_english_theme_row(row):
            hits.append(index)
    return hits
