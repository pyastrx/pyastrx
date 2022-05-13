"""Functions for searching the XML from file, file contents, or directory."""


from itertools import repeat
import os
from rich import print

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


def search(
        directory, expression, print_matches=False, print_xml=True,
        verbose=False, abspaths=False, recurse=True,
        extension=".py",
        before_context=4, after_context=4
):
    """
    Perform a recursive search through Python files.

    Only for files in the given directory for items matching the specified
    expression.
    """

    print("\n")
    if os.path.isfile(directory):
        files = (('', None, [directory]),)
    elif recurse:
        files = os.walk(directory)
    else:
        files = ((directory, None, [
            item
            for item in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, item))
        ]),)
    global_matches = []
    for root, __, filenames in files:
        python_filenames = (
            os.path.join(root, filename)
            for filename in filenames
            if filename.endswith(extension)
        )
        for filename in python_filenames:
          
            with open(filename, 'r') as f:
                content = f.read()
            file_lines = content.splitlines()
            matching_lines = search_in_txt(
                content, expression, filename, print_xml, verbose=verbose)
            global_matches.extend(zip(repeat(filename), matching_lines))

            if print_matches:
                stdout_matches(
                    matching_lines, filename, file_lines,
                    before_context, after_context, abspaths)

    return global_matches


