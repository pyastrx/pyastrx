"""Convert AST to XML objects."""

import ast
from lxml import etree
import codecs
from numbers import Number
from functools import partial
from rich import print


def _set_encoded_literal(set_fn, literal):
    if isinstance(literal, Number):
        literal = str(literal)
    try:
        set_fn(codecs.encode(literal, 'ascii', 'xmlcharrefreplace'))
    except Exception:
        set_fn('')  # Null byte - failover to empty string


def _strip_docstring(body):
    first = body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Str):
        return body[1:]
    return body


def convert_to_xml(node, omit_docstrings=False, node_mappings=None):
    """Convert supplied AST node to XML."""
    possible_docstring = isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module))

    xml_node = etree.Element(node.__class__.__name__)
    for attr in ('lineno', 'col_offset'):
        value = getattr(node, attr, None)
        if value is not None:
            _set_encoded_literal(
                partial(xml_node.set, attr),
                value
            )
    if node_mappings is not None:
        node_mappings[xml_node] = node

    node_fields = zip(
        node._fields,
        (getattr(node, attr) for attr in node._fields)
    )

    for field_name, field_value in node_fields:
        if isinstance(field_value, ast.AST):
            field = etree.SubElement(xml_node, field_name)
            field.append(
                convert_to_xml(
                    field_value,
                    omit_docstrings,
                    node_mappings,
                )
            )

        elif isinstance(field_value, list):
            field = etree.SubElement(xml_node, field_name)
            if possible_docstring and omit_docstrings and field_name == 'body':
                field_value = _strip_docstring(field_value)

            for item in field_value:
                if isinstance(item, ast.AST):
                    field.append(
                        convert_to_xml(
                            item,
                            omit_docstrings,
                            node_mappings,
                        )
                    )
                else:
                    subfield = etree.SubElement(field, 'item')
                    _set_encoded_literal(
                        partial(setattr, subfield, 'text'),
                        item
                    )

        elif field_value is not None:
            ## add type attribute e.g. so we can distinguish strings from numbers etc
            ## in older Python (< 3.8) type could be identified by Str vs Num and s vs n etc
            ## e.g. <Constant lineno="1" col_offset="6" type="int" value="1"/>
            _set_encoded_literal(
                partial(xml_node.set, 'type'),
                type(field_value).__name__
            )
            _set_encoded_literal(
                partial(xml_node.set, field_name),
                field_value
            )

    return xml_node


def contents2ast(
        contents: str, filename: str = "<unknown>", 
        verbose: bool = True) -> ast.Module:
    """Convert Python file contents (as a string) to an AST.

    Args:
        contents (str): Python file contents.
        filename (str): Filename to use in error messages.
        verbose (bool): If True, print error messages.
    Returns:
        ast.Module: AST of the supplied contents.

    """
    parsed_ast = ast.parse(contents, filename)
    if verbose:
        print(ast.dump(parsed_ast, indent=4))
    return parsed_ast
