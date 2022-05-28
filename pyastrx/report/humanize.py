"""This module is used to produce human-readable reports string for
the linter.

"""
from typing import List, Tuple

from pyastrx.config import __color_highlight, __severity2color
from pyastrx.data_typing import CodeContext, Lines2Matches, RuleInfo, RulesDict


def match_description(rule: RuleInfo) -> str:
    severity = rule.severity
    try:
        color = __severity2color[severity]
    except KeyError:
        color = __severity2color["default"]

    why = rule.why
    name = rule.name
    description = rule.description
    match_header_str = f"[bold {color}] - {name}|"\
        + f"{why} |"\
        + f"{description}"\
        + f"[/bold {color}]\n"
    return match_header_str


def str_context(
    context: CodeContext, line_match: int, cols: List[int]
) -> str:
    output_str = ""
    for (line_num), line_str in context:
        line_is_match = line_num == line_match
        should_highlight = line_is_match and len(context) > 1
        if line_is_match:
            line_mark_list = [" "] * len(line_str)
            for col_number in cols:
                line_mark_list[col_number] = "^"
            line_mark = ''.join(line_mark_list)
            line_mark = f"{'':<5}{line_mark}"
        if should_highlight:
            line_str = f"{f' {line_num}:':<5}{line_str}"
            output_str += f"[{__color_highlight}]"
            output_str += f"{line_str}[/{__color_highlight}]\n"
        else:
            output_str += f"{f' {line_num}:':<5}{line_str}\n"
        if line_is_match:
            output_str += f"{line_mark}\n"

    output_str += "-" * 20+"\n"
    return output_str


def matches_by_filename(
    line2matches: Lines2Matches,
    filename: str,
    rules: RulesDict,
) -> Tuple[str, int]:
    output_str = ""
    output_list = [f"[bold white on green]File:{filename}[/bold white on green]\n"] # noqa
    num_matches = 0
    for line_match, matches_by_line in line2matches.matches.items():
        context = matches_by_line.code_context
        cols = []
        for expr, match in matches_by_line.match_by_expr.items():
            col_numbers = match.cols_by_line[line_match]
            cols.extend(col_numbers)
            num_matches += 1
            rule_info = rules[expr]
            output_list += [match_description(rule_info)]
        output_list += [str_context(context, line_match, cols)]
    if len(output_list) > 1:
        output_str = "".join(output_list)

    return output_str, num_matches
