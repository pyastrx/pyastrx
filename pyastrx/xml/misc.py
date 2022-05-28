"""Module for XML misc functions like printing."""
from lxml import etree
from typing import Union
from io import BytesIO
from pyastrx.data_typing import AXML


def el_lxml2str(
        el_lxml: AXML, pretty_print: bool = True) -> str:
    "Convert lxml element to string."
    axml: Union[etree._Element, etree._ElementTree]
    if isinstance(el_lxml, bytes):
        axml = etree.parse(BytesIO(el_lxml))
    else:
        axml = el_lxml
    return str(etree.tostring(axml, pretty_print=pretty_print), "utf-8")
