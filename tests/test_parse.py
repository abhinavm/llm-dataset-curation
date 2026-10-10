from curation.parse import strip_gutenberg_boilerplate

SAMPLE = """The Project Gutenberg eBook of Example Book

This ebook is for the use of anyone anywhere in the United States and
most other parts of the world at no cost and with almost no restrictions
whatsoever.

*** START OF THE PROJECT GUTENBERG EBOOK EXAMPLE BOOK ***

Chapter 1

It was a dark and stormy night, and the data pipeline had been running
for seventeen hours straight.

*** END OF THE PROJECT GUTENBERG EBOOK EXAMPLE BOOK ***

*** END: FULL LICENSE ***

This and all associated files of various formats will be found in...
"""


def test_strips_header_and_footer():
    body = strip_gutenberg_boilerplate(SAMPLE)
    assert "Project Gutenberg" not in body
    assert "data pipeline had been running" in body
    assert "FULL LICENSE" not in body


def test_passes_through_text_with_no_markers():
    text = "Just plain text with no Gutenberg markers at all."
    assert strip_gutenberg_boilerplate(text) == text
