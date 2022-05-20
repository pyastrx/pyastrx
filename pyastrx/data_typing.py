"""This modules contains dataclasses and aditional
stuff to deal with data typing.

"""
from dataclasses import dataclass

from lxml import etree


@dataclass
class FileInfo:
    filename: str
    axml: etree._Element
    txt: str
    last_modified: float