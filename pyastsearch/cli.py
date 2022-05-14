#!/usr/bin/python

"""
The Command Line Interface using argparse.

For more help use::

    astpath -h

"""
import os
from pathlib import Path
import argparse
import yaml
from pyastsearch.search import search_in_folder, search_in_file
from pyastsearch.config import __available_yaml, __available_yaml_folder


def construct_base_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--quiet",
        help="hide output of matches",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "-x",
        "--xml",
        help="print only the matching XML elements",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--abspaths",
        help="show absolute paths",
        action="store_true",
    )
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
        "-A",
        "--after-context",
        help="lines of context to display after matching line",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-B",
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


def pyxpathlinter():
    parser = construct_base_argparse()
    args = parser.parse_args()
    config = {}
    invoke_pyastsearch(args, config)


def pyastsearch():
    parser = construct_base_argparse()
    args = parser.parse_args()
    config = {}
    invoke_pyastsearch(args, config)


def invoke_pyastsearch(args, extra_config):
    yml_file = Path(".").resolve() / ".pyastsearch.yaml"
    expr = args.expr
    if isinstance(expr, str):
        expr = [expr]
    config = {}
    if os.path.isfile(yml_file):
        with open(yml_file, "r") as f:
            yaml_config = yaml.safe_load(f)
        if len(expr) == 0:
            rules = yaml_config.get("rules", False)
            if rules:
                expr = rules
    if len(expr) == 0:
        raise ValueError("No rules or expression provided")

    config["rules"] = expr
    for key, val in __available_yaml.items():
        config[key] = yaml_config.get(key, val)
    config = {**config, **extra_config}
    if args.file != "":
        search_in_file(
            filename=args.file,
            **config
        )
    else:
        for key, val in __available_yaml_folder.items():
            config[key] = yaml_config.get(key, val)
        print(config)
        search_in_folder(
            **config,
        )


