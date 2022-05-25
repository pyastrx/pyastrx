from sys import version_info
import ast
from pathlib import Path
from typing import Tuple

import gast


def txt2ast(
        txt: str, filename: str = "<unknown>",
        normalize_ast: bool = True) -> ast.Module:
    """Convert Python file contents (as a string) to an AST.

    Args:
        txt (str): Python file contents.
        filename (str): Filename to use in error messages.
        normalize_ast (bool): Normalize the AST by using gast
            gast allows different python version to have the same AST.
            Which allows us to use the same kind of xpath queries.
    Returns:
        ast.Module: AST of the supplied contents.

    """
    if normalize_ast:
        parsed_ast = gast.parse(txt, filename)
    else:
        parsed_ast = ast.parse(txt, filename)

    return parsed_ast


def txt2ASTtxt(
        txt: str, normalize_ast: bool,
        indent: int = 2, filename: str = "<unknown>") -> str:
    """Construct the ast txt representation from a code string.

    Args:
        txt (str): Python file contents.
        indent (int): Indentation level.
        filename (str): Filename to use in error messages.
        normalize_ast (bool): Normalize the AST by using gast
            gast allows different python version to have the same AST.
            Which allows us to use the same kind of xpath queries.
    Returns:
        str: string representation of the AST.

    """
    ast_obj = txt2ast(txt, filename, normalize_ast)
    if version_info.minor < 9:
        return f"{ast.dump(ast_obj)}"
    return f"{ast.dump(ast_obj, indent=indent)}"


def file2ast(
        filename: str, normalize_ast: bool) -> Tuple[ast.AST, float]:
    """Construct the ast from a python file.

    Args:
        filename (str): Filename to use in error messages.
        normalize_ast (bool): Normalize the AST by using gast
            gast allows different python version to have the same AST.
            Which allows us to use the same kind of xpath queries.
    Returns:
        (ast.AST, float): AST of the supplied contents.

    """
    file_path = Path(filename)
    # get last modified time
    last_modified = file_path.stat().st_mtime
    with open(filename, "r") as f:
        txt = f.read()
    parsed_ast = txt2ast(txt, filename, normalize_ast=normalize_ast)
    return parsed_ast, last_modified
