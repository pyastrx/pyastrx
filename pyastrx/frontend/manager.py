import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

from rich import print as rprint
from pyastrx.data_typing import (
    Config,
    Files2Matches,
    RuleInfo,
    RulesDict,
    DataClassJSONEncoder,
)
from pyastrx.report import humanize as humanized_report
from pyastrx.report.stdout import rich_paging
from pyastrx.search.main import Repo

from dataclasses import dataclass


@dataclass
class MatchNode:
    match_str: str
    context: str
    line: int
    col: int


@dataclass
class FileNode:
    file: str
    match: Union[MatchNode, None] = None


def matches2vscode_ext(rules, file2matches, filter_rules):
    rules_infos = {
        k: v.__dict__
        for k, v in rules.items() if filter_rules[k] > 0}
    rule_map = {k: i for i, k in enumerate(rules_infos.keys())}
    files2save = {
        file: v.matches
        for file, v in file2matches.items()
        if len(v.num_matches_by_expr) > 0
    }
    rule_nodes = [
        {
            "expression": expr,
            "name": rule_info["name"],
            "severity": rule_info["severity"],
            "description": rule_info["description"],
            "why": rule_info["why"],
            "use_in_linter": rule_info["use_in_linter"],
            "files": [],
            "rules": [],
        }
        for expr, rule_info in rules_infos.items()
    ]

    for (file_name, matches_by_file) in files2save.items():
        for (line_number_str, matches_by_line) in matches_by_file.items():
            line_number = int(line_number_str)
            code_context = matches_by_line.code_context
            match_by_expr = matches_by_line.match_by_expr
            for (expr, match_pos) in match_by_expr.items():
                rule_id = rule_map.get(expr)
                matchNode = MatchNode(
                    match_str="",
                    context="",
                    line=0,
                    col=0,
                )

                fileNode = FileNode(
                    file=file_name,
                    match=matchNode,
                )
                context = ""
                match_str = ""
                cols = match_pos.cols_by_line[line_number]
                # iterate over code_contexy Array and
                for line_number_ctx, line_code in code_context:
                    context += line_code + "\n"
                    if line_number != line_number_ctx:
                        continue
                    match_str = line_code
                    lenLine = len(line_code)
                    carrets = " " * lenLine
                    for j in range(len(cols)):
                        carrets = carrets[: cols[j]] + "^" + carrets[cols[j] + 1 :] # noqa
                    context += carrets + "\n"

                fileNode.match.match_str = match_str
                fileNode.match.context = context
                fileNode.match.line = line_number
                fileNode.match.col = cols[0]
                # convert all dataclass to dict
                if rule_id is not None:
                    rule_nodes[rule_id]["files"].append(fileNode.__dict__)
    return rule_nodes


class Manager:
    def __init__(self, config: Config, repo: Repo) -> None:
        self.config = config
        self.repo = repo
        self._expression = ""
        self._current_rule: RulesDict = RulesDict({})
        self.selected_rules: List[str] = []

    @property
    def expression(self) -> str:
        return self._expression

    @expression.setter
    def expression(self, xpath: str) -> None:
        self._expression = xpath

    def resset_custom_expression(self) -> None:
        self._expression = ""

    def set_xpath_selection(self, xpath_keys: List[str]) -> None:
        self.selected_rules = xpath_keys

    def set_rule(self, xpath: str) -> bool:
        self.expression = xpath
        if xpath in self.config.rules.keys():
            self._current_rule = RulesDict({xpath: self.config.rules[xpath]})
            return True
        self._current_rule = RulesDict({xpath: RuleInfo()})
        return False

    def get_current_rules(self) -> RulesDict:
        if self._expression:
            return self._current_rule

        rules = self.config.rules
        if len(self.selected_rules) > 0:
            rules = RulesDict({k: rules[k] for k in self.selected_rules})

        if self.config.linter:
            return RulesDict({
                k: v for k, v in rules.items() if v.use_in_linter})
        return rules

    def filter_rules(self, num_matches_by_expr: Dict[str, int]) -> None:
        for expression, num_matches in num_matches_by_expr.items():
            if num_matches > 0:
                continue
            self.selected_rules = []
            del self.config.rules[expression]

    def set_current_file(self, file: str) -> None:
        info = self.repo.cache.get(file)
        self.current_fileinfo = info

    def load_specitications(self) -> None:
        self.repo.load_specifications(
            self.config.specifications,
        )
        files = self.repo.get_files()
        if len(files) > 1:
            return

        self.set_current_file(self.repo.get_file())

    def is_unique_file(self) -> bool:
        return len(self.repo.get_files()) == 1

    def is_folder(self) -> bool:
        return len(self.repo.get_files()) > 1

    def search(self) -> Tuple[int, Dict[int, Tuple[str, str]], Dict[str, int]]:
        rules = self.get_current_rules()
        is_unique_file = self.is_unique_file()
        config = self.config
        num_matches = 0
        str_by_file = {}
        parent_folder = Path(".").resolve()
        filter_rules = {k: 0 for k in rules.keys()}
        file2matches: Files2Matches
        if is_unique_file:
            file = self.repo.get_file()
            line2matches = self.repo.search_file(
                file,
                rules,
                before_context=config.before_context,
                after_context=config.after_context,
            )
            file2matches = Files2Matches({file: line2matches})

        else:
            file2matches = self.repo.search_files(
                rules,
                before_context=config.before_context,
                after_context=config.after_context,
                parallel=config.parallel,
            )

        output_str = ""
        for i, (file, line2matches) in enumerate(file2matches.items()):
            if len(line2matches.matches) == 0:
                continue
            for expr in line2matches.num_matches_by_expr.keys():
                filter_rules[expr] += line2matches.num_matches_by_expr[expr]
            output_str_file, num_matches_file = humanized_report.matches_by_filename( # noqa
                line2matches, file, rules
            )
            if num_matches_file > 0:
                str_by_file[i] = (
                    str(Path(file).relative_to(parent_folder)),
                    output_str_file,
                )
                num_matches += num_matches_file
                output_str += output_str_file
        # save json_data to
        if config.vscode_output:
            json_data = matches2vscode_ext(rules, file2matches, filter_rules)
            with open(Path(".pyastrx/results.json").resolve(), "w") as f:
                json.dump(json_data, f, cls=DataClassJSONEncoder)

        num_files = len(str_by_file)
        if not config.interactive:
            if not config.quiet:
                rprint(output_str)
            return num_matches, str_by_file, filter_rules

        interactive_files = config.interactive_files and num_files > 1
        if not interactive_files:
            if self.config.pagination:
                rich_paging(output_str)
            else:
                rprint(output_str)

        return num_matches, str_by_file, filter_rules
