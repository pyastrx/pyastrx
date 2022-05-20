import ast
from pathlib import Path
from typing import Tuple


def txt2ast(
        txt: str, filename: str = "<unknown>") -> ast.Module:
    """Convert Python file contents (as a string) to an AST.

    Args:
        txt (str): Python file contents.
        filename (str): Filename to use in error messages.
    Returns:
        ast.Module: AST of the supplied contents.

    """
    parsed_ast = ast.parse(txt, filename)
    return parsed_ast


def txt2ASTtxt(
        txt: str, indent: int = 2, filename: str = "<unknown>") -> str:
    """Construct the ast from a python file.

    Args:
        txt (str): Python file contents.
        indent (int): Indentation level.
        filename (str): Filename to use in error messages.
    Returns:
        str: string representation of the AST.

    """
    ast_obj = txt2ast(txt, filename)
    ast_txt = f"{ast.dump(ast_obj, indent=indent)}"
    return ast_txt


def file2ast(
        filename: str) -> Tuple[ast.AST, str]:
    """Construct the ast from a python file.

    Args:
        filename (str): Filename to use in error messages.
    Returns:
        (ast.AST, str): AST of the supplied contents.

    """
    file_path = Path(filename)
    # get last modified time
    last_modified = file_path.stat().st_mtime

    with open(filename, "r") as f:
        txt = f.read()
    parsed_ast = txt2ast(txt, filename)
    return parsed_ast, last_modified
