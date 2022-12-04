from pathlib import Path
from typing import Union
from lxml import etree

from pyastrx.axml.yaml.loader import Loader
from pyastrx.data_typing import FileInfo


def file2axml(
        filename: str,
        specification_name: str,
        baxml: bool = False,
) -> FileInfo:
    """Construct the FileInfo obj from a yaml file.

    """
    file_path = str(Path(filename).resolve())
    with open(file_path, "r") as f:
        txt = f.read()
    loader = Loader(txt)

    xml_yaml: Union[etree._Element, etree._ElementTree]
    xml_yaml = loader \
        .get_single_node() \
        .xml_node(module_node=True, file_path=file_path)

    if not baxml:
        info = FileInfo(
            filename=file_path,
            axml=xml_yaml,
            txt=txt,
            language="yaml",
            specification_name=specification_name
        )
        return info

    xml_yamlb = etree.tostring(xml_yaml, encoding="utf-8")
    info = FileInfo(
        filename=file_path,
        axml=xml_yamlb,
        txt=txt,
        language="yaml",
        specification_name=specification_name
    )
    return info
