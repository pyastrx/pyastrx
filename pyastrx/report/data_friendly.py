from pyastrx.data_typing import Files2Matches, Lines2Matches


def extract_lines(
    lines2matches: Lines2Matches,
    filename: str,
) -> dict:
    rules = {}
    for line, matches_by_line in lines2matches.items():
        code_context = matches_by_line.code_context
        context_str = "\n".join(code for line, code in code_context)
        match_str = [code for l, code in code_context if line == line]
        for expression, match in matches_by_line.match_by_expr.items():
            data = {
                    "line": line,
                    "file": filename,
                    "col":  match.cols_by_line[line][0],
                    "context": context_str,
                    "match_str": match_str
                }
            if expression not in rules:
                rule_infos = match.rule_info
                rules[expression] = {"rule_infos": rule_infos, "matches": []}

            rules[expression]["matches"].append(data)
    return rules


def vscode_dict(file2matches: Files2Matches) -> dict:
    """This function is used to generate a dictionary that
    later can be converted to json and sent to VSCode Extension.

    """
    data = {}
    for i, (filename, lines2matches) in enumerate(
            file2matches.items()):
        rules_by_file = extract_lines(lines2matches, filename)
        for expression, rule in rules_by_file.items():
            rule_infos = rule["rule_infos"]
            matches = rule["matches"]
            if expression not in data:
                data[expression] = {
                    "name": rule_infos.name,
                    "severity": rule_infos.severity,
                    "description": rule_infos.description,
                    "why": rule_infos.why,
                    "files": []
                }
            data_file = {
                "file": filename,
                "matches": []
            }
            for match in matches:
                data_file["matches"].append(match)
            data[expression]["files"].append(data_file)
    data_root = {
        "root": [
            {"expression": expression, **value}
            for expression, value in data.items()
        ]
    }
    return data_root