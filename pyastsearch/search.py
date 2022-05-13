"""Functions for searching the XML from file, file contents, or directory."""


from itertools import repeat
import os
from rich import print

from pyastsearch.xml_tools import linenos_from_xml
from pyastsearch.ast_tools import convert_to_xml, contents2ast
from pyastsearch.outputs import stdout_matches, stdout_xml


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
        if recurse:
            raise ValueError("Cannot recurse when only a single file is specified.")
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
            node_mappings = {}
            try:
                with open(filename, 'r') as f:
                    contents = f.read()
                file_lines = contents.splitlines()
                parsed_ast = contents2ast(contents, filename, verbose=verbose)
                xml_ast = convert_to_xml(
                    parsed_ast,
                    omit_docstrings=False,
                    node_mappings=node_mappings,
                )
                
            except Exception:
                if verbose:
                    print("WARNING: Unable to parse or read {}".format(
                        os.path.abspath(filename) if abspaths else filename
                    ))
                continue  # unparseable

            matching_elements = xml_ast.xpath(expression)

            if print_xml:
                stdout_xml(matching_elements, xml_ast)

            matching_lines = linenos_from_xml(matching_elements, node_mappings=node_mappings)
            global_matches.extend(zip(repeat(filename), matching_lines))

            if print_matches:
                stdout_matches(
                    matching_lines, filename, file_lines, before_context, after_context, abspaths)

    return global_matches


