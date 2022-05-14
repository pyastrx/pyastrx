#!/usr/bin/python

"""
The Command Line Interface using argparse.

For more help use::

    astpath -h

"""

import os
import argparse
import yaml
from pyastsearch.search import search_in_dir, search_in_file


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
        "-d",
        "--dir",
        help="search directory",
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
        "expr",
        help="search expression",
        nargs="+",
    )
    args = parser.parse_args()

    before_context = args.before_context or args.context
    after_context = args.after_context or args.context
    if (before_context or after_context) and args.quiet:
        print("ERROR: Context cannot be specified when suppressing output.")
        exit(1)
    expr = " ".join(args.expr)
    if args.file != "":
        search_in_file(
            args.file,
            expr,
            args.quiet,
            args.verbose,
            args.xml,
            args.abspaths,
            before_context,
            after_context,
        )
    else:
        search_in_dir(
            args.dir,
            expr,
            print_xml=args.xml,
            print_matches=not args.quiet,
            verbose=args.verbose,
            abspaths=args.abspaths,
            recurse=args.recursive,
            before_context=before_context,
            after_context=after_context,
        )


if __name__ == "__main__":
    main()
