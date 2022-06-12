#!/usr/bin/env python
"""
Script to run the mypy inference engine
in the command line.

"""
import argparse
from rich import print as rprint

from pyastrx.inference.mypy import infer_types as infer_types_mypy


def mypy_query() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--files",
        help="files to perform the query",
        type=str,
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--raw-output",
        help="Display the output without any formatting",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    files = args.files
    query_results, success = infer_types_mypy(files)
    if not success:
        return

    if args.raw_output:
        print(query_results)
        return

    for result in query_results:
        rprint(result["path"])
        rprint(result["types"])


if __name__ == "__main__":
    mypy_query()
