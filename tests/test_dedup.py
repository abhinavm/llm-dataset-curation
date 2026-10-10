from curation import dedup


def test_exact_dedup_drops_identical_text():
    docs = [
        ("a", "The quick brown fox jumps over the lazy dog."),
        ("b", "The quick brown fox jumps over the lazy dog."),
        ("c", "Something completely different."),
    ]
    kept = list(dedup.exact_dedup(docs))
    assert [doc_id for doc_id, _ in kept] == ["a", "c"]


def test_exact_dedup_ignores_whitespace_and_case():
    docs = [
        ("a", "Hello   World"),
        ("b", "hello world"),
    ]
    kept = list(dedup.exact_dedup(docs))
    assert len(kept) == 1


def test_near_dedup_catches_near_duplicates():
    base = "the quick brown fox jumps over the lazy dog in the park every single morning without fail"
    near_copy = base.replace("park", "field")
    docs = [
        ("a", base),
        ("b", near_copy),
        ("c", "totally unrelated text about distributed systems and spark clusters and shuffle joins"),
    ]
    result = dedup.near_dedup(docs, threshold=0.5)
    assert "a" in result.kept_ids
    assert "b" in result.dropped_ids
    assert "c" in result.kept_ids
