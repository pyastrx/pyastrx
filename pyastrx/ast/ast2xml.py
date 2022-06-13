from typing import Callable, Union, Any, Optional, List
import ast
import codecs
from functools import partial
from numbers import Number
from pathlib import Path
import re

from lxml import etree

from pyastrx.ast.things2ast import txt2ast
from pyastrx.data_typing import ASTrXType, FileInfo, AXML


def set_encoded_literal(
        set_fn: Callable[[Union[str, bytes]], None],
        literal: Union[Number, str]) -> None:
    if isinstance(literal, Number):
        literal = str(literal)
    try:
        set_fn(codecs.encode(literal, "ascii", "xmlcharrefreplace"))
    except Exception:
        set_fn("")  # Null byte - failover to empty string


def encode_type(
    xml_node: etree._Element,
    field_name: str,
    field_value: Any,
    infered_types: List[ASTrXType],
    el_loc: List[int]
) -> None:
    num_types = len(infered_types)
    i = 0
    encoded = False

    while i < num_types:
        infered_type = infered_types[i]
        annotation = infered_type["annotation"]
        loc = infered_type["location"]
        location = [
            loc["start"]["line"],
            loc["start"]["column"],
            loc["stop"]["line"],
            loc["stop"]["column"]
        ]
        if all(a == b for a, b in zip(location, el_loc)):
            set_encoded_literal(
                partial(xml_node.set, "type"), annotation
            )
            for attr_name in ("name", "node_name", "fullname"):
                value = getattr(field_value, attr_name, None)
                if value is None:
                    continue
                xml_node.set(attr_name, value)
            attrs = infered_type["attrs"]
            if attrs is None:
                continue
            for attr in attrs:
                xml_node.set(attr, "1")
            encoded = True
            break
        i += 1
    if not encoded:
        # no reason to try to encode type using this method
        # if is not a Constant node
        if xml_node.tag != "Constant":
            return
        set_encoded_literal(
            partial(xml_node.set, "type"), type(field_value).__name__
        )


def transformer_ast_node_field(
        field_value: Any, field_name: str, xml_node: etree._Element,
        infered_types: Optional[List[ASTrXType]] = None,
        txt_lines: Optional[List[str]] = None,
        el_loc: Optional[List[int]] = None
) -> None:
    if field_name == "annotation" and infered_types:
        return
    if isinstance(field_value, ast.AST):
        field = etree.SubElement(xml_node, field_name)
        field.append(
            ast2xml(
                field_value,
                infered_types=infered_types,
                txt_lines=txt_lines,
                el_loc_parent=el_loc
            )
        )

    elif isinstance(field_value, list):
        field = etree.SubElement(xml_node, field_name)
        for item in field_value:
            if isinstance(item, ast.AST):
                field.append(
                    ast2xml(
                        item,
                        infered_types=infered_types,
                        txt_lines=txt_lines,
                        el_loc_parent=el_loc
                    )
                )
            else:
                subfield: etree._Element = etree.SubElement(field, "item")
                set_encoded_literal(partial(setattr, subfield, "text"), item)
    elif field_value is not None:
        set_encoded_literal(
            partial(xml_node.set, field_name), field_value)

        if infered_types is None or el_loc is None:
            # this encondes int, str, float that in python 3 grammar
            # are Const nodes with the type information
            if xml_node.tag != "Constant":
                return
            set_encoded_literal(
                partial(xml_node.set, "type"), type(field_value).__name__
            )
            return
        encode_type(
            xml_node,
            field_value=field_value,
            field_name=field_name,
            infered_types=infered_types,
            el_loc=el_loc,
        )


def encode_location(
        node: Union[ast.AST, ast.Module], xml_node: etree._Element,
        txt_lines: Optional[List[str]] = None) -> None:
    """This encode the code location available in the AST node
    into the XML node.

    """

    # the below code is used because the location obtained from the
    # pyre is based on the tokens position for some types of nodes like
    # ClassDef, FunctionDef, etc.
    if node.__class__.__name__ in (
            "FunctionDef", "ClassDef", "arg") and txt_lines:
        value = getattr(node, "name", None)
        if value is None:
            value = getattr(node, "arg", None)
        lineno = node.lineno
        txt_line = txt_lines[lineno-1]
        rc = re.compile(f"{value}(?!([0-9]|\\_|^a-zA-Z))") # noqa
        r_result = rc.search(txt_line)
        if r_result is None:
            return

        end_col_offset = r_result.end()
        col_offset = r_result.start()
        setattr(node, "end_lineno", lineno)
        setattr(node, "end_col_offset", end_col_offset)
        setattr(node, "col_offset", col_offset)

    for attr in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
        value = getattr(node, attr, None)
        if value is None:
            continue
        set_encoded_literal(partial(xml_node.set, attr), value)


def ast2xml(
        node: ast.AST,
        txt_lines: Optional[List[str]] = None,
        infered_types: Optional[List[ASTrXType]] = None,
        el_loc_parent: Optional[List[int]] = None
) -> etree._Element:
    """Convert supplied AST node to XML."""

    #  ast_node_name can be for example "FunctionDef", "ClassDef"...
    ast_node_name = node.__class__.__name__
    xml_node = etree.Element(ast_node_name)
    node_fields = zip(
        node._fields, (getattr(node, attr) for attr in node._fields))
    encode_location(
        node, xml_node, txt_lines)

    try:
        el_loc = [
                int(xml_node.get(attr, 0))
                for attr in (
                    "lineno", "col_offset", "end_lineno", "end_col_offset")
        ]
    except TypeError:
        if el_loc_parent:
            el_loc = el_loc_parent
        else:
            el_loc = []

    for field_name, field_value in node_fields:
        transformer_ast_node_field(
            field_value, field_name, xml_node,
            infered_types=infered_types,
            txt_lines=txt_lines,
            el_loc=el_loc
        )

    return xml_node


def file2axml(
        filename: str,
        infered_types: Optional[List[ASTrXType]] = None,
        normalize_ast: bool = True,
        baxml: bool = False,
) -> FileInfo:
    """Construct the FileInfo obj from a python file.

    """
    file_path = str(Path(filename).resolve())
    with open(file_path, "r") as f:
        txt = f.read()
    parsed_ast = txt2ast(txt, file_path, normalize_ast)
    xml_ast: AXML
    txt_lines = None
    if infered_types:
        txt_lines = txt.split("\n")
    xml_ast = ast2xml(
        parsed_ast,
        txt_lines=txt_lines,
        infered_types=infered_types
    )
    if baxml:
        xml_ast = etree.tostring(xml_ast, encoding="utf-8")

    info = FileInfo(
        filename=file_path,
        axml=xml_ast,
        txt=txt,
    )

    return info
