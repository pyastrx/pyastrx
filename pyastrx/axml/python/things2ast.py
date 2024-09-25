import ast
import sys
from typing import Any

import gast


def txt2ast(
        txt: str, filename: str = "<unknown>",
        normalize_ast: bool = True) -> Any:
    """Convert Python file contents (as a string) to an AST.

    Args:
        txt (str): Python file contents.
        filename (str): Filename to use in error messages.
        normalize_ast (bool): Normalize the AST by using gast
            gast allows different python version to have the same AST.
            Which allows us to use the same kind of xpath queries.
    Returns:
        parsed_ast: AST of the supplied contents.
            Any if from gast.
            Module if from ast.

    """

    # this is a hack to deal with the fact that ast.parse
    # can't handle with syntax errors, we try to remove the line
    # with the error until the end of the file to see if we can
    # parse the file.

    parsed = False
    num_tries = 0
    while not parsed:
        try:
            if normalize_ast:
                parsed_ast = gast.parse(txt, filename)
            else:
                parsed_ast = ast.parse(txt, filename)
            parsed = True
        except SyntaxError as e:
            lineno = e.lineno
            if num_tries > 1:
                # return a empty ast
                return ast.parse("")
            lines = txt.split("\n")
            # remove all the lines after the error
            if lineno is not None:
                lines = lines[:lineno-1]
                txt = "\n".join(lines)
            num_tries += 1

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
    if sys.version_info >= (3, 9):
        return f"{ast.dump(ast_obj, indent=indent)}"
    else:
        return f"{ast.dump(ast_obj)}"


def file2ast(
        filename: str, normalize_ast: bool) -> ast.AST:
    """Construct the ast from a python file.

    Args:
        filename (str): Filename to use in error messages.
        normalize_ast (bool): Normalize the AST by using gast
            gast allows different python version to have the same AST.
            Which allows us to use the same kind of xpath queries.
    Returns:
        ast.AST

    """
    with open(filename, "r") as f:
        txt = f.read()
    parsed_ast = txt2ast(txt, filename, normalize_ast=normalize_ast)
    return parsed_ast
