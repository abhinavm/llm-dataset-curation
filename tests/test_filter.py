from curation.filter import FilterConfig, passes_quality_filter


def test_rejects_too_short():
    result = passes_quality_filter("too short")
    assert not result.passed
    assert result.reason.startswith("too_short")


def test_rejects_high_symbol_ratio():
    text = ("word " * 60) + ("#" * 200)
    result = passes_quality_filter(text)
    assert not result.passed
    assert result.reason.startswith("high_symbol_ratio")


def test_rejects_repetitive_lines():
    lines = ["subscribe to our newsletter"] * 20 + ["one different line here"]
    text = "\n".join(lines)
    result = passes_quality_filter(text)
    assert not result.passed
    assert result.reason.startswith("repetitive_lines")


def test_accepts_normal_prose():
    text = " ".join(["this is a perfectly normal sentence about data engineering"] * 10)
    result = passes_quality_filter(text)
    assert result.passed


def test_custom_config_changes_threshold():
    text = " ".join(["word"] * 10)
    assert not passes_quality_filter(text).passed
    lenient = FilterConfig(min_words=5)
    assert passes_quality_filter(text, lenient).passed
