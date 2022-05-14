"""Functions for searching the XML from file, file contents, or directory."""
import os
import multiprocessing as mp
from functools import partial
from pathlib import Path

from pyastsearch.xml_tools import linenos_from_xml
from pyastsearch.ast_tools import convert_to_xml, txt2ast
from pyastsearch.outputs import stdout_matches, stdout_xml


def search_in_txt(
        txt, expression, filename="<unknown>", print_xml=False, verbose=False):
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

    matching_lines = linenos_from_xml(
        matching_elements, node_mappings=node_mappings)
   
    return matching_lines


def search_in_file(filename, expression, print_xml=False, verbose=False):
    with open(filename, 'r') as f:
        content = f.read()
    file_lines = content.splitlines()
    matching_lines = search_in_txt(
        content, expression, filename, print_xml, verbose=verbose)
    return filename, file_lines, matching_lines


def search(
        directory, expression, print_matches=False, print_xml=True,
        verbose=False, abspaths=False, recurse=True,
        extension="py",
        before_context=0, after_context=0,
        parallel=True,
        exclude_dirs=[".venv"]
):
    """
    Perform a recursive search through Python files.

    Only for files in the given directory for items matching the specified
    expression.
    """
    if os.path.isfile(directory):
        files = [directory]
    else:
        if recurse:
            files = Path(directory).rglob(f'*.{extension}')
        else:
            files = Path(directory).glob(f'*.{extension}')
        files = [
            f for f in files 
            if not any(d in f.parts for d in exclude_dirs)
        ]
    if parallel:
        with mp.Pool() as pool:
            results = pool.map(
                partial(
                    search_in_file,
                    expression=expression, print_xml=print_xml, verbose=verbose
                ),
                files
            )
        file2matches = {}
        for filename, file_lines, matching_lines in results:
            file2matches[filename] = (file_lines, matching_lines)

    else:
        file2matches = {}
        for filename in files:          
            filename, file_lines, matching_lines = search_in_file(
                filename, expression, print_xml, verbose=verbose) 
            file2matches[filename] = (file_lines, matching_lines)

    if print_matches:
        stdout_matches(
            file2matches, before_context, after_context, abspaths=abspaths)

    file2linenos = {
        filename: linenos for filename, (_, linenos) in file2matches.items()
    }
    return file2linenos