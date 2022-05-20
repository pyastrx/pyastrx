"""Module for XML misc functions like printing."""
from lxml import etree


def el_lxml2str(
        el_lxml: etree._Element, pretty_print: bool = True) -> str:
    "Convert lxml element to string."
    return str(etree.tostring(el_lxml, pretty_print=pretty_print), "utf-8")