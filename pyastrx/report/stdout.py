"""This module has the methods that can produce a nice and
    readable report on stdout.
"""
import pydoc

from lxml import etree
from rich.console import Console

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


def paging_lxml(el_lxml: etree._Element) -> None:
    "Use rich to page the lxml element through less and pydoc."
    text = el_lxml2str(el_lxml)
    rich_paging(text)