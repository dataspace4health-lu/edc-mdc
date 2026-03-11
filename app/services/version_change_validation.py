from typing import Iterable, Optional


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip()
    return normalized if normalized else None


def normalize_version_notes(version_notes: Iterable[object] | None) -> set[str]:
    normalized_notes: set[str] = set()
    for note in version_notes or set():
        note_value = note.value if hasattr(note, "value") else note
        if not isinstance(note_value, str):
            continue

        normalized = note_value.strip()
        if normalized:
            normalized_notes.add(normalized)

    return normalized_notes
