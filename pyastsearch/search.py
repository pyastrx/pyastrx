"""Functions for searching the XML from file, file contents, or folder."""
import multiprocessing as mp
from functools import partial
from pathlib import Path

from pyastsearch.xml_tools import linenos_from_xml
from pyastsearch.ast_tools import convert_to_xml, txt2ast
from pyastsearch.outputs import stdout_matches, stdout_xml, stdout_matches_by_filename


def search_in_txt(
    txt, expression, filename="<unknown>", print_xml=False, verbose=False
):
    """Search in source code string and return the matching lines.

    Args:
        txt (str): The source code to search.
        expression (str): The search expression.
        filename (str): The filename to use in the output.
        print_xml (bool): Print the XML of the AST.
        verbose (bool): Verbose output.
    Returns:
        list: The matching lines.
    """

    node_mappings = {}

    parsed_ast = txt2ast(txt, filename, verbose=verbose)
    xml_ast = convert_to_xml(
        parsed_ast,
        omit_docstrings=False,
        node_mappings=node_mappings,
    )
    matching_elements = xml_ast.xpath(expression)
    if print_xml:
        stdout_xml(matching_elements, xml_ast)

    matching_lines = linenos_from_xml(matching_elements, node_mappings=node_mappings)

    return matching_lines


def get_matches_in_file(filename, expression, print_xml=False, verbose=False):
    """Get the matching lines in a file.

    Args:
        filename (str): The filename to search.
        expression (str): The search expression.
        print_xml (bool): Print the XML of the AST.
        verbose (bool): Verbose output.
    Returns:
        (str, list, list): The filename, the lines of the file, and the matching lines.

    """
    with open(filename, "r") as f:
        content = f.read()
    file_lines = content.splitlines()
    matching_lines = search_in_txt(
        content, expression, filename, print_xml, verbose=verbose
    )
    return filename, file_lines, matching_lines


def search_in_file(
    filename,
    expression,
    print_xml=False,
    verbose=False,
    print_matches=False,
    before_context=0,
    after_context=0,
    abspaths=False,
):
    """Search in a file and return the matching lines as well show the matches
    in stdout.

    Args:
        filename (str): The filename to search.
        expression (str): The search expression.
        print_xml (bool): Print the XML of the AST.
        verbose (bool): Verbose output.
        print_matches (bool): Print the matches in stdout.
        before_context (int): Lines of context to display before matching line.
        after_context (int): Lines of context to display after matching line.
        abspaths (bool): Print absolute paths.
    Returns:
        list: The matching lines.
    """

    filename, file_lines, matching_lines = get_matches_in_file(
        filename, expression, print_xml, verbose
    )
    if len(matching_lines) > 0 and print_matches:
        print("\n")
        stdout_matches_by_filename(
            matching_lines,
            filename,
            file_lines,
            before_context,
            after_context,
            abspaths,
        )
        print(f"[bold red]{'='*15}End of {filename}{'='*15}[/bold red]")
        print("\n\n")
    return matching_lines


def search_in_folder(
    folder,
    expression,
    print_matches=False,
    print_xml=True,
    verbose=False,
    abspaths=False,
    recurse=True,
    extension="py",
    before_context=0,
    after_context=0,
    parallel=True,
    exclude_folders=[".venv"],
):
    """Search in a folder and return the matching lines as well show the matches
    in stdout.

    Args:
        folder (str): The folder to search.
        expression (str): The search expression.
        print_matches (bool): Print the matches in stdout.
        print_xml (bool): Print the XML of the AST.
        verbose (bool): Verbose output.
        abspaths (bool): Print absolute paths.
        recurse (bool): Recurse into subdirectories.
        extension (str): The extension to search.
        before_context (int): Lines of context to display before matching line.
        after_context (int): Lines of context to display after matching line.
        parallel (bool): Use multiprocessing.
        exclude_folders (list): List of directories to exclude.

    Returns:
        dict: The filename is the key, and the value is the matching lines.

    """

    if recurse:
        files = Path(folder).rglob(f"*.{extension}")
    else:
        files = Path(folder).glob(f"*.{extension}")
    files = [f for f in files if not any(d in f.parts for d in exclude_folders)]
    if parallel:
        with mp.Pool() as pool:
            results = pool.map(
                partial(
                    get_matches_in_file,
                    expression=expression,
                    print_xml=print_xml,
                    verbose=verbose,
                ),
                files,
            )
        file2matches = {}
        for filename, file_lines, matching_lines in results:
            file2matches[filename] = (file_lines, matching_lines)

    else:
        file2matches = {}
        for filename in files:
            filename, file_lines, matching_lines = get_matches_in_file(
                filename, expression, print_xml, verbose=verbose
            )
            file2matches[filename] = (file_lines, matching_lines)

    if print_matches:
        stdout_matches(file2matches, before_context, after_context, abspaths=abspaths)

    file2linenos = {
        filename: linenos for filename, (_, linenos) in file2matches.items()
    }
    return file2linenos
