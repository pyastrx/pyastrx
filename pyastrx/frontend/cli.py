#!/usr/bin/python
"""
The Command Line Interface for PyASTrix.

"""
import os
from pathlib import Path
import argparse
import yaml
from pyastrx.config import __available_yaml, __available_yaml_folder
from pyastrx.frontend.state_machine import Context, StartState
from memory_profiler import profile


def construct_base_argparse():
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
        "-l",
        "--linter",
        help= "Run in the linter mode. "\
            + "No interactive mode, all the rules "\
            + "with use_in_linter=false will be ignored",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--folder",
        help="search folder",
        default=".",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="search in a file",
        default="",
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


def pyastrx():
    parser = construct_base_argparse()
    args = parser.parse_args()
    config = {}
    invoke_pyastrx(args, config)


def get_config_from_yaml() -> dict:
    """Will check if .pyastrx.yaml exists in the current directory.
    If it does, it will load the config from it. If not, it will
    create a new one with the default values.

    """
    yml_file = Path(".").resolve() / ".pyastrx.yaml"
    if not yml_file.exists():
        config = __available_yaml
        with open(yml_file, "w") as f:
            f.write(yaml.dump(config))
        return config

    with open(yml_file, "r") as f:
        config = yaml.safe_load(f)

    return config

@profile
def invoke_pyastrx(args, extra_config):
    expr = args.expr
    if isinstance(expr, str):
        expr = [expr]
    config = {}
    yaml_config = get_config_from_yaml()
    if len(expr) == 0:
        rules = yaml_config.get("rules", False)
        if rules:
            expr = rules
        else:
            expr = {}

    config["interactive"] = args.interactive
    config["rules"] = expr
    for key, val in __available_yaml.items():
        if key not in config:
            config[key] = yaml_config.get(key, val)
    if args.linter:
        config["linter"] = True
        config["interactive"] = False

    if len(expr) == 0 and config["interactive"] == False:
        raise ValueError("No rules or expression provided")

    config = {**config, **extra_config}
    config["file"] = ""
    if args.file != "":
        config["file"] = args.file
    if config["file"] == "":
        for key, val in __available_yaml_folder.items():
            config[key] = yaml_config.get(key, val)

    sm = Context(initial_state=StartState(), config=config)
    while True:
        sm._state.run()
