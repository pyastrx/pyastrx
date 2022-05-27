from itertools import islice
from typing import List

from pyastrx.data_typing import CodeContext


def apply_context(
        lines: List[str],
        index: int, before: int = 0, after: int = 0) -> CodeContext:
    start = max(0, index - before)
    end = index + 1 + after
    context_list = CodeContext([
        (i+1, line) for i, line in islice(enumerate(lines), start, end)
    ])

    return context_list
