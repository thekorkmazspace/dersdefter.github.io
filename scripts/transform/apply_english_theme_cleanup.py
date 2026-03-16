#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.common.paths import DATA_DIR
from scripts.transform.english_theme_cleanup import (
    find_mixed_english_theme_rows,
    normalize_english_theme_rows,
)


JSON_PLANLAR_DIR = REPO_ROOT / "json_planlar"
DATA_JSON_PLANLAR_DIR = DATA_DIR / "json_planlar"
TARGET_FIELDS = ("ÜNİTE", "KONU", "KAZANIM")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def changed_row_indices(original_rows: list[dict], normalized_rows: list[dict]) -> list[int]:
    indices = []
    for index, (original_row, normalized_row) in enumerate(
        zip(original_rows, normalized_rows),
        start=1,
    ):
        if any(original_row.get(field) != normalized_row.get(field) for field in TARGET_FIELDS):
            indices.append(index)
    return indices


def apply_changes_to_peer(path: Path, normalized_rows: list[dict], row_indices: list[int]) -> bool:
    if not path.exists():
        return False

    payload = load_json(path)
    peer_rows = payload.get("plan", [])
    if len(peer_rows) != len(normalized_rows):
        raise ValueError(f"Satır sayısı uyuşmuyor: {path}")

    changed = False
    for row_index in row_indices:
        peer_row = peer_rows[row_index - 1]
        normalized_row = normalized_rows[row_index - 1]

        for field in ("ÜNİTE", "KONU"):
            if peer_row.get(field) != normalized_row.get(field):
                peer_row[field] = normalized_row.get(field)
                changed = True

        peer_kazanim = str(peer_row.get("KAZANIM", "")).strip()
        if peer_kazanim and peer_row.get("KAZANIM") != normalized_row.get("KAZANIM"):
            peer_row["KAZANIM"] = normalized_row.get("KAZANIM")
            changed = True

    if changed:
        write_json(path, payload)
    return changed


def main() -> int:
    modified_files: list[str] = []

    for data_path in sorted(DATA_DIR.glob("*ingilizce*.json")):
        if data_path.name in {"index.json", "official_names.json"}:
            continue

        payload = load_json(data_path)
        original_rows = payload.get("plan", [])
        mixed_rows = find_mixed_english_theme_rows(original_rows)
        if not mixed_rows:
            continue

        normalized_rows = normalize_english_theme_rows(original_rows)
        row_indices = changed_row_indices(original_rows, normalized_rows)
        if not row_indices:
            continue

        payload["plan"] = normalized_rows
        write_json(data_path, payload)
        modified_files.append(f"data/{data_path.name}: {row_indices}")

        for peer_root in (JSON_PLANLAR_DIR, DATA_JSON_PLANLAR_DIR):
            peer_path = peer_root / data_path.name
            if apply_changes_to_peer(peer_path, normalized_rows, row_indices):
                modified_files.append(f"{peer_path.relative_to(REPO_ROOT)}: {row_indices}")

    if not modified_files:
        print("English theme cleanup: değişiklik yok.")
        return 0

    print("English theme cleanup tamamlandı:")
    for item in modified_files:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
