#!/usr/bin/env python
"""Pre-commit hook for PyASTrix.

"""

import sys
import subprocess


if __name__ == "__main__":
    files = sys.argv
    if len(files) == 0:
        print("No files to check")
        exit(0)
    exit_code = 0
    for f in files:
        process = subprocess.Popen(
            ["pyastrx", "-l", "-f", f"{f}"],
            shell=False
        )
        process.communicate()
        exit_code += process.wait()

    sys.exit(exit_code)

