from pathlib import Path
from typing import Union
from lxml import etree
import yaml

from rich import print as print
from pyastrx.axml.yaml.loader import Loader
from pyastrx.data_typing import FileInfo


def txt2axml(
    txt: str,
    file_path: str = "",
) -> Union[etree._Element, etree._ElementTree]:

    xml_yaml: Union[etree._Element, etree._ElementTree]

    parsed = False
    num_tries = 0
    while not parsed:
        try:
            loader = Loader(txt)
            xml_yaml = loader.get_single_node().get_xml_node(
                module_node=True, file_path=file_path
            )
            parsed = True
        except yaml.scanner.ScannerError as err:
            if err.problem_mark is None:
                break
            lineno = err.problem_mark.line
            if num_tries > 1:
                # return a empty ast
                xml_yaml = etree.Element("Module")
                break
            lines = txt.split("\n")
            # remove all the lines after the error
            lines = lines[:lineno -1]
            txt = "\n".join(lines)
            num_tries += 1
        except AttributeError as err:
            print(err)
            xml_yaml = etree.Element("Module")
            break

    return xml_yaml


def file2axml(
    filename: str,
    specification_name: str,
    baxml: bool = False,
) -> FileInfo:
    """Construct the FileInfo obj from a yaml file."""
    file_path = str(Path(filename).resolve())
    with open(file_path, "r") as f:
        txt = f.read()

    xml_yaml = txt2axml(txt, file_path=file_path)

    if not baxml:
        info = FileInfo(
            filename=file_path,
            axml=xml_yaml,
            txt=txt,
            language="yaml",
            specification_name=specification_name,
        )
        return info

    xml_yamlb = etree.tostring(xml_yaml, encoding="utf-8")
    info = FileInfo(
        filename=file_path,
        axml=xml_yamlb,
        txt=txt,
        language="yaml",
        specification_name=specification_name,
    )
    return info
