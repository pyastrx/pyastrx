import ast
import codecs
from functools import partial
from numbers import Number
from pathlib import Path

from lxml import etree

from pyastrx.ast.things2ast import txt2ast
from pyastrx.data_typing import FileInfo


def _set_encoded_literal(set_fn, literal) -> None:
    if isinstance(literal, Number):
        literal = str(literal)
    try:
        set_fn(codecs.encode(literal, "ascii", "xmlcharrefreplace"))
    except Exception:
        set_fn("")  # Null byte - failover to empty string


def transformer_ast_node_field(field_value, field_name, xml_node):
    if isinstance(field_value, ast.AST):
        field = etree.SubElement(xml_node, field_name)
        field.append(
            ast2xml(
                field_value,
            )
        )

    elif isinstance(field_value, list):
        field = etree.SubElement(xml_node, field_name)
        for item in field_value:
            if isinstance(item, ast.AST):
                field.append(
                    ast2xml(
                        item,
                    )
                )
            else:
                subfield = etree.SubElement(field, "item")
                _set_encoded_literal(partial(setattr, subfield, "text"), item)

    elif field_value is not None:
        _set_encoded_literal(
            partial(xml_node.set, "type"), type(field_value).__name__
        )
        _set_encoded_literal(
            partial(xml_node.set, field_name), field_value)


def encode_location(node: ast.AST, xml_node: etree.Element) -> None:
    """This encode the code location available in the AST node
    into the XML node.

    """
    # for attr in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
    for attr in ("lineno", "col_offset"):
        value = getattr(node, attr, None)
        if value is None:
            continue
        _set_encoded_literal(partial(xml_node.set, attr), value)


def ast2xml(node: ast.AST) -> etree.Element:
    """Convert supplied AST node to XML."""

    xml_node = etree.Element(node.__class__.__name__)
    encode_location(node, xml_node)

    node_fields = zip(
        node._fields, (getattr(node, attr) for attr in node._fields))

    for field_name, field_value in node_fields:
        transformer_ast_node_field(field_value, field_name, xml_node)

    return xml_node


def file2axml(
        filename: str, normalize_ast: bool) -> FileInfo:
    """Construct the FileInfo obj from a python file.

    """
    file_path = Path(filename)
    last_modified = file_path.stat().st_mtime
    with open(filename, "r") as f:
        txt = f.read()
    parsed_ast = txt2ast(txt, filename, normalize_ast)
    xml_ast = ast2xml(
        parsed_ast,
    )
    info = FileInfo(
        filename=filename,
        axml=xml_ast,
        txt=txt,
        last_modified=last_modified,
    )

    return info
