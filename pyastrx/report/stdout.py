"""This module has the methods that can produce a nice and
    readable report on stdout.
"""
import pydoc
from typing import Union
from io import BytesIO

from lxml import etree
from rich.console import Console

from pyastrx.data_typing import AXML
from pyastrx.xml.misc import el_lxml2str


def rich_paging(text: str) -> None:
    "Use rich to page the text through less and pydoc."
    if text == "":
        return
    console = Console()
    with console.capture() as capture:
        console.print(text)
    str_output = capture.get()
    pydoc.pipepager(str_output, cmd='less -R')


def paging_lxml(el_lxml: AXML) -> None:
    "Use rich to page the lxml element through less and pydoc."
    axml: Union[etree._Element, etree._ElementTree]
    if isinstance(el_lxml, bytes):
        axml = etree.parse(BytesIO(el_lxml))
    else:
        axml = el_lxml
    text = el_lxml2str(axml)
    rich_paging(text)
