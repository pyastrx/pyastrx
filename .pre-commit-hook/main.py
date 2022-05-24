#!/usr/bin/env python
"""Pre-commit hook for PyASTrix.

"""

import sys
import subprocess

if __name__ == "__main__":
    files = [
        f for f in sys.argv if f.endswith(".py")
    ]
    if len(files) == 0:
        print("No files to check")
        exit(0)
    commands = ["pyastrx", "-l", "-f", *files]
    if "-q" in sys.argv:
        commands.append("-q")
    process = subprocess.Popen(
        commands,
        shell=False
    )
    process.communicate()
    exit_code = process.wait()

    sys.exit(exit_code)

