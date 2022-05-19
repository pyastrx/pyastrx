from itertools import islice


def apply_context(
        lines, index: int, before: int = 0, after: int = 0):
    """
    Yield of 2-tuples from lines around the index. Like grep -A, -B, -C.

    before and after are ignored if a value for both is set. Example usage::

        >>>list(context('abcdefghij', 5, before=1, after=2))
        [(4, 'e'), (5, 'f'), (6, 'g'), (7, 'h')]



    """
    start = max(0, index - before)
    end = index + 1 + after
    context_list = [
        (i+1, line) for i, line in islice(enumerate(lines), start, end)
    ]

    return context_list

