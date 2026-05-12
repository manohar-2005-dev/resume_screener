'''from src.ingestion.loader import load_resume

test_files = [
    "data/samples/resume_DS_Intern.pdf",
    "data/samples/resume_DS_Intern.docx",
    "data/samples/resume_DS_Intern.txt",
]

for file in test_files:
    result = load_resume(file)
    if result:
        print(f"\n✅ {result['file_name']}")
        print(f"   Type   : {result['file_type']}")
        print(f"   Status : {result['status']}")
        print(f"   chars  : {len(result['raw_text'])}")
        print(f"   Preview: {result['raw_text'][:150]}")
    else:
        print(f"\n❌ Failed to load {file}")'''
import sys
import os
#import pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.ingestion.loader import load_resume
from src.preprocessing.parser import parse_resume
from src.chunking.splitter import chunk_resume
from src.embeddings.vectorstore import (
    store_chunks, search_similar, clear_vectorstore
)
from src.matching.engine import screen_candidate, save_results


# ══════════════════════════════════════════════════════
# TEST 1 — INGESTION
# ══════════════════════════════════════════════════════

def test_load_pdf_returns_dict():
    """PDF loader should return a dict with raw_text."""
    result = load_resume("data/samples/resume_DS_Intern.pdf")
    assert result is not None
    assert "raw_text" in result
    assert len(result["raw_text"]) > 100

def test_load_invalid_file_returns_none():
    """Loading a non-existent file should return None gracefully."""
    result = load_resume("data/samples/fake_resume.pdf")
    assert result is None

def test_load_unsupported_format_returns_none():
    """Unsupported file formats should return None."""
    result = load_resume("data/samples/resume.xyz")
    assert result is None


# ══════════════════════════════════════════════════════
# TEST 2 — PARSING
# ══════════════════════════════════════════════════════

def test_parse_returns_required_fields():
    """Parser should return all required fields."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])

    required_fields = [
        "name", "email", "phone",
        "skills", "experience", "education",
        "github", "linkedin", "raw_text"
    ]
    for field in required_fields:
        assert field in parsed, f"Missing field: {field}"

def test_parse_email_is_valid():
    """Extracted email should contain @ symbol."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    assert parsed["email"] is not None
    assert "@" in parsed["email"]

def test_parse_skills_is_list():
    """Skills should be a non-empty list."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    assert isinstance(parsed["skills"], list)
    assert len(parsed["skills"]) > 0

def test_parse_phone_is_10_digits():
    """Phone number should be exactly 10 digits."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    if parsed["phone"]:
        assert len(parsed["phone"]) == 10
        assert parsed["phone"].isdigit()


# ══════════════════════════════════════════════════════
# TEST 3 — CHUNKING
# ══════════════════════════════════════════════════════

def test_chunks_created():
    """Resume should produce at least 3 chunks."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]
    chunks = chunk_resume(parsed)
    assert len(chunks) >= 3

def test_chunk_has_required_keys():
    """Each chunk must have text, chunk_id, candidate_name."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]
    chunks = chunk_resume(parsed)

    for chunk in chunks:
        assert "text" in chunk
        assert "chunk_id" in chunk
        assert "candidate_name" in chunk
        assert len(chunk["text"]) > 0

def test_no_duplicate_chunk_ids():
    """All chunk IDs must be unique."""
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]
    chunks = chunk_resume(parsed)

    ids = [chunk["chunk_id"] for chunk in chunks]
    assert len(ids) == len(set(ids)), "Duplicate chunk IDs found"


# ══════════════════════════════════════════════════════
# TEST 4 — VECTOR STORE
# ══════════════════════════════════════════════════════

def test_store_and_search():
    """Stored chunks should be retrievable by semantic search."""
    clear_vectorstore()

    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]
    chunks = chunk_resume(parsed)
    store_chunks(chunks)

    results = search_similar("Python machine learning", n_results=3)
    assert len(results) > 0
    assert "text" in results[0]
    assert "candidate_name" in results[0]

def test_search_returns_relevant_chunks():
    """Search for Python should return chunks mentioning Python."""
    results = search_similar("Python data science", n_results=3)
    combined_text = " ".join([r["text"] for r in results]).lower()
    assert "python" in combined_text


# ══════════════════════════════════════════════════════
# TEST 5 — SCORE CONSISTENCY
# ══════════════════════════════════════════════════════

def test_score_is_valid_range():
    """Match score must be between 0 and 100."""
    clear_vectorstore()

    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]

    jd = "Python developer with machine learning experience"
    result = screen_candidate(parsed, jd)

    assert 0 <= result["match_score"] <= 100

def test_recommendation_is_valid():
    """Recommendation must be one of the four valid values."""
    clear_vectorstore()

    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]

    jd = "Python developer with machine learning experience"
    result = screen_candidate(parsed, jd)

    valid_recommendations = ["Strong Yes", "Yes", "Maybe", "No"]
    assert result["recommendation"] in valid_recommendations


# ══════════════════════════════════════════════════════
# TEST 6 — EDGE CASES
# ══════════════════════════════════════════════════════

def test_parse_empty_text_does_not_crash():
    """Parser should handle empty string without crashing."""
    result = parse_resume("")
    assert isinstance(result, dict)
    assert result["email"] is None
    assert result["skills"] == []

def test_save_results_creates_file():
    """save_results should create a JSON file on disk."""
    dummy_results = [{
        "candidate_name": "Test User",
        "match_score": 75,
        "recommendation": "Yes"
    }]
    file_path = save_results(dummy_results, job_title="Test Role")
    assert os.path.exists(file_path)
    assert file_path.endswith(".json")