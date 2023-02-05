from pyastrx.search.txt_tools import apply_context


def test_apply_context():
    """Test the apply_context function."""
    lines = [
        "def apply_context(",
        "        lines: List[str],",
        "        index: int, before: int = 0, after: int = 0) -> CodeContext:",
        "    start = max(0, index - before)",
        "    end = index + 1 + after",
        "    context_list = CodeContext([",
        "        (i+1, line) for i, line in islice(enumerate(lines), start, end)",
        "    ])",
        "",
        "    return context_list",
        "",
    ]
    index = 2
    before = 2
    after = 2
    context_list = apply_context(lines, index, before, after)
    assert context_list == [
        (1, "def apply_context("),
        (2, "        lines: List[str],"),
        (3, "        index: int, before: int = 0, after: int = 0) -> CodeContext:"),
        (4, "    start = max(0, index - before)"),
        (5, "    end = index + 1 + after"),
    ]
