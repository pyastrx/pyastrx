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
from pyastsearch.config import __default_expr_info


def main():
    """Entrypoint for CLI."""
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
        "-C",
        "--context",
        help="lines of context to display before and after matching line",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--expr",
        help="search expression",
        nargs="+",
        default=[],
    )
    args = parser.parse_args()

    before_context = args.before_context or args.context
    after_context = args.after_context or args.context
    if (before_context or after_context) and args.quiet:
        print("ERROR: Context cannot be specified when suppressing output.")
        exit(1)

    yml_file = Path(".").resolve() / ".pyastsearch.yaml"
    exclude_folders = [".venv"]
    expr_list = args.expr
    expr = {e: __default_expr_info.copy() for e in expr_list}
    if os.path.isfile(yml_file):
        with open(yml_file, "r") as f:
            config = yaml.safe_load(f)
            exclude_folders = config.get("exclude_folders", exclude_folders)
            rules = config.get("rules", False)
            if rules:
                expr = rules
    else:
        config = {}

    folder = config.get("folder", args.folder)
    quiet = config.get("quiet", args.quiet)
    verbose = config.get("verbose", args.verbose)
    xml = config.get("xml", args.xml)
    abspaths = config.get("abspaths", args.abspaths)
    recursive = config.get("recursive", args.recursive)
    after_context = config.get("after_context", after_context)
    before_context = config.get("before_context", before_context)
    abspaths = config.get("abspaths", args.abspaths)
    parallel = config.get("parallel", args.parallel)

    if isinstance(expr, str):
        expr = [expr]

    if args.file != "":
        search_in_file(
            args.file,
            expr,
            quiet,
            verbose,
            xml,
            abspaths,
            before_context,
            after_context,
        )
    else:
        search_in_folder(
            folder,
            expr,
            print_xml=xml,
            print_matches=True,
            verbose=verbose,
            abspaths=abspaths,
            recurse=recursive,
            before_context=before_context,
            after_context=after_context,
            exclude_folders=exclude_folders,
            parallel=parallel,
        )


if __name__ == "__main__":
    main()
