#!/usr/bin/env python
"""
The Command Line Interface for PyASTrix.

"""
import argparse
from pathlib import Path

import yaml

from pyastrx.config import __available_yaml, __available_yaml_folder
from pyastrx.data_typing import (
    Config, MatchParams, RuleInfo, RulesDict, InferenceConfig)
from pyastrx.frontend.manager import Manager
from pyastrx.frontend.state_machine import Context, StartState
from pyastrx.search.main import Repo


def multiLine2line(multi_line_xpath: str) -> str:
    """Formatter for a xpath str from a yaml.

    This allows to use indentation and multiple lines to
    define complex xpath expressions

    """
    # Remove spaces in the beginning of each line
    lines = [v.lstrip() for v in multi_line_xpath.split("\n")]
    xpath = "".join(lines)
    return xpath


def construct_base_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-R",
        "--recursive",
        help="subdirectories search",
        action="store_false",
    )
    parser.add_argument(
        "-p",
        "--parallel",
        help="disable parallel search",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="interactive mode",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-n",
        "--no-interface",
        help="disable CLI interface",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--vscode-output",
        help="This saves the output in a format that can be read by VSCode PyASTrX extension", # noqa
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--linter",
        help="""Run in the linter mode.
            No interactive mode, all the rules
            with use_in_linter=false will be ignored""",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Do not print the results.",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--folder",
        help="search folder",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="search in a file or list of files",
        type=str,
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "-a",
        "--after-context",
        help="lines of context to display after matching line",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-b",
        "--before-context",
        help="lines of context to display after matching line",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--expr",
        help="search expression",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--exclude",
        help="exclude folders",
        nargs="+",
        default=[".venv"],
    )
    return parser


def pyastrx() -> None:
    parser = construct_base_argparse()
    args = parser.parse_args()
    invoke_pyastrx(args)


def get_config_from_yaml() -> dict:
    """Will check if pyastrx.yaml exists in the current directory.
    If it does, it will load the config from it. If not, it will
    create a new one with the default values.

    """
    yml_file = Path(".").resolve() / "pyastrx.yaml"
    if not yml_file.exists():
        config = __available_yaml
        with open(yml_file, "w") as f:
            f.write(yaml.dump(config))
        return config

    with open(yml_file, "r") as f:
        config = yaml.safe_load(f)

    return config


def invoke_pyastrx(args: argparse.Namespace) -> None:
    rules: RulesDict
    config = {}
    yaml_config = get_config_from_yaml()
    if len(args.expr) > 0:
        rules = RulesDict({str(e): RuleInfo() for e in args.expr})

    else:
        rules_yaml = yaml_config.get("rules", {})
        rules_dict = {}
        for name, v in rules_yaml.items():
            xpath = multiLine2line(v["xpath"])
            del v["xpath"]
            v["name"] = name
            rules_dict[xpath] = RuleInfo(**v)
        rules = RulesDict(rules_dict)

    config["interactive"] = args.interactive
    config["rules"] = rules
    for key, val in __available_yaml.items():
        if key not in config:
            config[key] = yaml_config.get(key, val)
    if args.linter:
        config["linter"] = True
        config["interactive"] = False
    if args.quiet:
        config["quiet"] = True
        config["interactive"] = False

    if args.no_interface:
        config["interactive"] = False
    if args.vscode_output:
        config["vscode_output"] = True

    if len(rules) == 0 and config["interactive"] is False:
        raise ValueError(
                "No rules found in the yaml file and no expression provided")

    config["files"] = args.file
    for key, val in __available_yaml_folder.items():
        config[key] = yaml_config.get(key, val)
    if args.folder:
        config["folder"] = args.folder
    if args.vscode_output:
        config["vscode_output"] = True
    config_pyastrx = Config(**config)

    match_params = MatchParams(
        **yaml_config.get("match_params", {})
    )
    inference = InferenceConfig(**yaml_config.get("inference", {}))

    file_cache: bool = yaml_config.get("file_cache", True)
    repo = Repo(match_params, inference, file_cache=file_cache)
    if not config_pyastrx.interactive:
        manager = Manager(config_pyastrx, repo)
        manager.load_files()
        num_matches = manager.search()[0]
        if config_pyastrx.linter:
            exit_code = 1 if num_matches > 0 else 0
            exit(exit_code)
        return
    else:
        sm = Context(
            initial_state=StartState, config=config_pyastrx, repo=repo)
        while True:
            sm._state.run()


if __name__ == "__main__":
    pyastrx()
