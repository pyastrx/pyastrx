"""Functions for searching the XML from file, file contents, or directory."""


from itertools import islice, repeat
import os
from rich import print
from lxml.etree import tostring

from pyastsearch.xml_tools import linenos_from_xml
from pyastsearch.ast_tools import convert_to_xml, contents2ast


def search(
        directory, expression, print_matches=False, print_xml=True,
        verbose=False, abspaths=False, recurse=True,
        extension=".py",
        before_context=0, after_context=0
):
    """
    Perform a recursive search through Python files.

    Only for files in the given directory for items matching the specified
    expression.
    """


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
                for element in matching_elements:
                    print(tostring(xml_ast, pretty_print=True))

            matching_lines = linenos_from_xml(matching_elements, node_mappings=node_mappings)
            global_matches.extend(zip(repeat(filename), matching_lines))

            if print_matches:
                for match in matching_lines:
                    matching_lines = list(context(
                        file_lines, match - 1, before_context, after_context
                    ))
                    for lineno, line in matching_lines:
                        print('{path}:{lineno:<5d}{sep}\t{line}'.format(
                            path=os.path.abspath(filename) if abspaths else filename,
                            lineno=lineno,
                            sep='>' if lineno == match - 1 else ' ',
                            line=line,
                        ))
                    if before_context or after_context:
                        print()

    return global_matches


def context(lines, index, before=0, after=0, both=0):
    """
    Yield of 2-tuples from lines around the index. Like grep -A, -B, -C.

    before and after are ignored if a value for both is set. Example usage::

        >>>list(context('abcdefghij', 5, before=1, after=2))
        [(4, 'e'), (5, 'f'), (6, 'g'), (7, 'h')]

    :arg iterable lines: Iterable to select from.
    :arg int index: The item of interest.
    :arg int before: Number of lines of context before index.
    :arg int after: Number of lines of context after index.
    :arg int both: Number of lines of context either side of index.
    """
    before, after = (both, both) if both else (before, after)
    start = max(0, index - before)
    end = index + 1 + after
    return islice(enumerate(lines), start, end)
