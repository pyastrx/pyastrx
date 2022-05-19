"""This module is used to produce human-readable reports string for
the linter.

"""
from typing import List, Tuple
from pyastrx.config import __severity2color, __color_highlight


def match_description(rule: dict) -> str:
    severity = rule.get("severity", "default")
    try:
        color = __severity2color[severity]
    except KeyError:
        color = __severity2color["default"]

    why = rule.get("why", "")
    name = rule.get("name", "")
    description = rule.get("description", "")
    match_header_str = f"[bold {color}] - {name}|"\
        + f"{why} |"\
        + f"{description}"\
        + f"[/bold {color}]\n"

    return match_header_str


def str_context(
    context: Tuple, line_match: int, cols: List
) -> str:
    output_str = ""
    for (line_num), line_str in context:
        line_is_match = line_num == line_match
        should_highlight = line_is_match and len(context) > 1
        if line_is_match:
            line_mark = [" "] * len(line_str)
            for col_number in cols:
                line_mark[col_number] = "^"
            line_mark = ''.join(line_mark)
            line_mark = f"{'':<5}{line_mark}"
        if should_highlight:
            line_str = f"{f' {line_num+1}:':<5}{line_str}"
            output_str += f"[{__color_highlight}]"
            output_str += f"{line_str}[/{__color_highlight}]\n"
        else:
            output_str += f"{f' {line_num+1}:':<5}{line_str}\n"
        if line_is_match:
            output_str += f"{line_mark}\n"

    output_str += "-" * 20+"\n"
    return output_str


def matches_by_filename(
    matching_rules_by_line: dict,
    filename: str,
) -> str:
    output_str = ""
    output_list = [f"[bold white on green]File:{filename}[/bold white on green]\n"]
    for line_match, context_and_rule in matching_rules_by_line.items():
        expressions = context_and_rule[1]
        context = context_and_rule[0]
        cols = []
        for _, info in expressions.items():
            col_numbers = info["col_nums"]
            rule_infos = info["rule_infos"]
            cols.extend(col_numbers)
            output_list += [match_description(rule_infos)]
        output_list += [str_context(context, line_match, cols)]
    if len(output_list) > 1:
        output_str = "".join(output_list)

    return output_str