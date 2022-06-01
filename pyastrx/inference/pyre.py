"""Responsible to extract the inference results from pyre.
"""
import subprocess
import json
from typing import Tuple, List

from pyastrx.data_typing import PyreFile


def infer_types(files: List[str], ) -> Tuple[List[PyreFile], bool]:
    """

    Args:
        files: list(str)
            List of files to be analyzed.
    Returns:
        Tuple[List[PyreFile], bool]
            - A list of PyreFile dicts. The list has
            the same length and order as the input files.
            - True if pyre successfully ran.

    """
    files_str = "".join([f"'{f}'," for f in files])[:-1]
    commands = ["pyre", "query", f"types({files_str})"]
    process = subprocess.Popen(
        commands,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    exit_code = process.wait()
    if exit_code != 0:
        print(stderr.decode("utf-8"))
        exit(exit_code)
    pyre_response = json.loads(stdout.decode("utf-8"))
    if "response" not in pyre_response:
        print(pyre_response)
        return [], False
    if len(pyre_response["response"]) == 0:
        print(pyre_response)
        return [], False

    return pyre_response["response"], True
