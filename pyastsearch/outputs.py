import os
from itertools import islice
from rich import print
from lxml.etree import tostring


def context(lines, index, before=0, after=0, both=0):
    """
    Yield of 2-tuples from lines around the index. Like grep -A, -B, -C.

    before and after are ignored if a value for both is set. Example usage::

        >>>list(context('abcdefghij', 5, before=1, after=2))
        [(4, 'e'), (5, 'f'), (6, 'g'), (7, 'h')]

    :arg iterable lines: Iterable to select from.
    :arg int index: The item of interest.
    :arg int before: Number of lines of context before index.
    :arg int after: Number of lines of context after index.
    :arg int both: Number of lines of context either side of index.
    """
    before, after = (both, both) if both else (before, after)
    start = max(0, index - before)
    end = index + 1 + after
    return islice(enumerate(lines), start, end)


def stdout_matches(
        matching_lines, filename, file_lines,
        before_context=0, after_context=0, abspaths=False,):
    path = os.path.abspath(filename) if abspaths else filename
    print(f"[bold green]File:{path}[/bold green]")
    for match in matching_lines:
        matching_lines_context = list(context(
            file_lines, match - 1, before_context, after_context
        ))
        for lineno, line in matching_lines_context:
            if lineno == match - 1:
                print(f"[white on yellow]{f'{lineno}:':<5}{line}[/white on yellow]")
            else:
                print(f"{f'{lineno}:':<5}{line}")
        if before_context or after_context:
            print()
        print("-"*20)


def stdout_xml(matching_elements, xml_ast):
    for _ in matching_elements:
        print(tostring(xml_ast, pretty_print=True))