import pytest
from pydantic import ValidationError
from matching_engine import mismatch_guard
from batch_processor import ImageMetadata

def test_schema_validation_catches_errors():
    bad_data = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["wild"],
        "caption": "A fox."
    }
    with pytest.raises(ValidationError):
        ImageMetadata(**bad_data)

def test_mismatch_guard_rejects_wolf_for_fox():
    post = {"title": "Red Foxes", "content": "Foxes are great."}
    candidate = {"subject": "wolves", "confidence": 0.95}
    approved, reason = mismatch_guard(post, candidate, 0.90)
    assert approved is False
    assert "expected fox, detected wolf" in reason

def test_mismatch_guard_approves_good_match():
    post = {"title": "Red Foxes", "content": "Foxes are great."}
    candidate = {"subject": "fox", "confidence": 0.95}
    approved, reason = mismatch_guard(post, candidate, 0.90)
    assert approved is True
