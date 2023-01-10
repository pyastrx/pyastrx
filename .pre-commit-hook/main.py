#!/usr/bin/env python
"""Pre-commit hook for PyASTrix.

"""

import subprocess
import sys

if __name__ == "__main__":
    files = [
        f for f in sys.argv if any(
            [f.endswith(f".{ext}") for ext in ("yaml", "yml", "py")]
        )
    ]
    if len(files) == 0:
        print("No files to check")
        exit(0)
    commands = ["pyastrx", "-l", "-f", *files]
    if "-q" in sys.argv:
        commands.append("-q")
    process = subprocess.Popen(
        commands,
        shell=True
    )
    process.communicate()
    exit_code = process.wait()

    sys.exit(exit_code)
