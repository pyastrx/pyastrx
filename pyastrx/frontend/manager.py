import json
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from rich import print as rprint

from pyastrx.config import __available_yaml as available_yaml
from pyastrx.data_typing import (
    Config, Files2Matches, RuleInfo, RulesDict,
    DataClassJSONEncoder)
from pyastrx.report import humanize as humanized_report
from pyastrx.report.stdout import rich_paging
from pyastrx.search.main import Repo


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
                k: v for k, v in rules.items()
                if v.use_in_linter})
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

    def load_files(self) -> None:
        parallel = self.config.parallel
        files = self.config.files
        if len(files) > 0:
            self.repo.load_files(
                files, normalize_ast=self.config.normalize_ast,
                parallel=parallel
            )
            if len(files) == 1:
                self.set_current_file(self.repo.get_files()[0])
        else:
            self.repo.load_folder(
                self.config.folder,
                normalize_ast=self.config.normalize_ast,
                parallel=parallel,
                exclude=self.config.exclude,
                recursive=self.config.recursive
            )

    def reload_yaml(self) -> None:
        with open(Path("pyastrx.yaml").resolve(), "r") as f:
            _config = yaml.safe_load(f)
        for k in ("rules", "interactive_files", "pagination"):
            if k not in _config.keys():
                _config[k] = available_yaml[k]
            else:
                setattr(self.config, k, _config[k])
        self.config.rules = RulesDict({
            k: RuleInfo(**v) for k, v in _config["rules"].items()
        })

    def is_unique_file(self) -> bool:
        return len(self.repo.get_files()) == 1

    def is_folder(self) -> bool:
        return len(self.repo.get_files()) > 1

    def search(self) -> Tuple[
            int, Dict[int, Tuple[str, str]], Dict[str, int]]:
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
                    file, rules,
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
        for i, (file, line2matches) in enumerate(
                file2matches.items()):
            if len(line2matches.matches) == 0:
                continue
            for expr in line2matches.num_matches_by_expr.keys():
                filter_rules[expr] += line2matches.num_matches_by_expr[expr]
            output_str_file, num_matches_file = \
                humanized_report.matches_by_filename(
                        line2matches, file, rules)
            if num_matches_file > 0:
                str_by_file[i] = (
                    str(Path(file).relative_to(parent_folder)),
                    output_str_file
                )
                num_matches += num_matches_file
                output_str += output_str_file
        # save json_data to
        if config.vscode_output:
            rule_infos = {
                k: v.__dict__ for k, v in rules.items()
                if filter_rules[k] > 0
            }

            json_data = {
                "files": {
                    file: v.matches
                    for file, v in file2matches.items()
                    if len(v.num_matches_by_expr) > 0
                },
                "rules": rule_infos,
            }
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
