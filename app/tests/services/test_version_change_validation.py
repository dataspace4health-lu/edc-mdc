from models.dataset import DatasetVersionNote
from services.version_change_validation import normalize_text, normalize_version_notes


def test_normalize_text_strips_and_handles_empty():
    assert normalize_text(" 1.0 ") == "1.0"
    assert normalize_text("   ") is None
    assert normalize_text(None) is None


def test_normalize_version_notes_accepts_model_objects_and_strings():
    notes = {
        DatasetVersionNote(value=" Initial "),
        "  Added field A  ",
        "",
        "   ",
    }

    assert normalize_version_notes(notes) == {"Initial", "Added field A"}


def test_normalize_version_notes_handles_none():
    assert normalize_version_notes(None) == set()
