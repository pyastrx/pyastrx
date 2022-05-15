import os
from itertools import islice
from rich import print as rprint
from lxml.etree import tostring
from colorama import Style
from pyastsearch.config import __severity2color, __color_highlight


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


def print_match_description(cols, rule):
    severity = rule.get("severity", "default")
    try:
        color = __severity2color[severity]
    except KeyError:
        color = __severity2color["default"]

    why = rule.get("why", "")
    name = rule.get("name", "")
    description = rule.get("description", "")
    cols_str = ",".join(map(str, cols))
    print(
        f"{color} - {name:<5}|",
        f"{why:<18}|",
        f"{description}{Style.RESET_ALL}",
        f"{Style.BRIGHT}{f'{cols_str}'}{Style.RESET_ALL}",
    )


def print_lines_context(
    matching_lines_context, line_match, after_context, before_context,
    cols,
):
    for (lineno), line in matching_lines_context:
        line_is_match = lineno == line_match - 1
        should_highlight = line_is_match and (
            after_context > 0 or before_context > 0
        )  # noqa
        if line_is_match:
            line_mark = [" "] * len(line)
            for col_number in cols:
                line_mark[col_number] = "^"
            line_mark = ''.join(line_mark)
            line_mark = f"{'':<5}{line_mark}"
        if should_highlight:
            line_str = f"{f' {lineno+1}:':<5}{line}"
            rprint(f"[{__color_highlight}]{line_str}[/{__color_highlight}]")
        else:
            rprint(f"{f' {lineno+1}:':<5}{line}")
        if line_is_match:
            rprint(f"{line_mark}")
    if before_context or after_context:
        print()
    rprint("-" * 20)


def stdout_matches_by_filename(
    matching_lines,
    filename,
    file_lines,
    before_context=0,
    after_context=0,
    abspaths=False,
):
    path = os.path.abspath(filename) if abspaths else filename
    line2expression = {}
    for expression, data in matching_lines.items():
        rule = data["rule_infos"]
        for line_match in matching_lines[expression]["lines"]:
            line_number = line_match[0]
            if line_number not in line2expression:
                line2expression[line_number] = {
                    expression: {"col_number": [], "rule_infos": rule}
                }
            else:
                line2expression[line_number][expression] = {
                    "col_number": [],
                    "rule_infos": rule,
                }
    for expression, rule in matching_lines.items():
        for line_match in matching_lines[expression]["lines"]:
            line_number = line_match[0]
            col_number = line_match[1]
            line2expression[line_number][expression]["col_number"].append(col_number)
    
    rprint(f"[bold white on green]File:{path}[/bold white on green]")
    #rprint(f"[bold white on green]Matches:{len(lines)}[/bold white on green]")

    for line_match, expressions in line2expression.items():
        # rules = line2expression[(line_match, col_number)]
        #rules = matching_lines[expression]["rule_infos"]
        cols = []
        for _, info in expressions.items():
            col_numbers = info["col_number"]
            rule_infos = info["rule_infos"]
            cols.extend(col_numbers)
            print_match_description(col_numbers, rule_infos)
        
        matching_lines_context = list(
            context(file_lines, line_match - 1, before_context, after_context)
        )
        print_lines_context(
            matching_lines_context, line_match, after_context, before_context, cols
        )


def stdout_matches(
    file2matches,
    before_context=0,
    after_context=0,
    abspaths=False,
):
    for filename, (file_lines, matching_lines) in file2matches.items():
        if len(matching_lines) == 0:
            continue
        stdout_matches_by_filename(
            matching_lines,
            filename,
            file_lines,
            before_context,
            after_context,
            abspaths,
        )

def stdout_xml(matching_elements, xml_ast):
    for _ in matching_elements:
        print(tostring(xml_ast, pretty_print=True))
