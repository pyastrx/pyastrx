import copyreg
from functools import partial
from io import BytesIO
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Tuple

from lxml import etree

from pyastrx.ast.ast2xml import file2axml
from pyastrx.data_typing import FileInfo
from pyastrx.search.cache import Cache
from pyastrx.search.txt_tools import apply_context
from pyastrx.search.xml_search import search_in_axml


def lxml_el_unpickle(el_lxml: bytes) -> etree._ElementTree:
    """Unpickle an lxml element.
    """
    el_lxml = etree.parse(BytesIO(el_lxml))
    return el_lxml


def lxml_el_pickle(el_lxml: etree._Element) -> Tuple[Callable, Tuple[bytes]]:
    """Pickle an lxml element.

    This is a custom pickle function that allows us to use lxml
    with multiprocessing.

    """
    data = etree.tostring(el_lxml)
    return lxml_el_unpickle, (data,)


# This registers the unpickling function for lxml elements.
copyreg.pickle(etree._Element, lxml_el_pickle, lxml_el_unpickle)
copyreg.pickle(etree._ElementTree, lxml_el_pickle, lxml_el_unpickle)


def search_in_file_info(
        file_info: FileInfo, rules: dict,
        before_context: int = 0, after_context: int = 0):
    if file_info is None:
        return {}

    matching_lines_by_rule = search_in_axml(
            rules,
            axml=file_info.axml)
    matching_rules_by_line = {}
    for expression, matching_lines in matching_lines_by_rule.items():
        line_nums = matching_lines["line_nums"]
        for line_num, cols in line_nums:
            if line_num not in matching_rules_by_line:
                matching_lines_context = apply_context(
                    file_info.txt.splitlines(), line_num - 1,
                    before_context, after_context)
                matching_rules_by_line[line_num] = [
                    matching_lines_context,
                    {
                        expression: {
                            "col_nums": cols,
                            "rule_infos": matching_lines["rule_infos"]
                        }
                    }
                ]
            else:
                matching_rules_by_line[line_num][1][expression] = {
                    "col_nums": cols,
                    "rule_infos": matching_lines["rule_infos"]
                }
    return matching_rules_by_line


class Repo:
    def __init__(self):
        self.cache = Cache()
        self.cache.load()

    def load_file(self, filename):
        info, _ = self.cache.update(filename)
        self._files = [filename]
        if not info:
            info = file2axml(filename)
            self.cache.set(filename, info)

    def search_file(
            self, filename, rules,
            before_context=0,
            after_context=0):
        info = self.cache.get(filename)
        if info is None:
            print(f"{filename} not found in cache")
            return {}
        matching_rules_by_line = search_in_file_info(
            info, rules, before_context, after_context)

        return matching_rules_by_line

    def load_folder(
        self,
        folder,
        recursive=True,
        parallel=True,
        extension="py",
        exclude_folders=None,
    ):
        if exclude_folders is None:
            exclude_folders = [".venv"]
        if recursive:
            files = Path(folder).rglob(f"*.{extension}")
        else:
            files = Path(folder).glob(f"*.{extension}")
        files = [
            str(f.resolve()) for f in files
            if not any(d in f.parts for d in exclude_folders)
        ]
        self.load_files(files, parallel)

    def load_files(
        self,
        files,
        parallel=True,
    ):

        files2load = [
            filename for filename in files
            if self.cache.update(filename)[0] is False
        ]
        if len(files2load) == 0:
            return

        if parallel:
            with Pool() as pool:
                infos = pool.map(
                        file2axml, files2load)
            for info, filename in zip(infos, files2load):
                if info is None:
                    raise Exception(f"Failed to convert {filename}")
                self.cache.set(filename, info)
        else:
            for filename in files2load:
                self.load_file(filename)

        self._files = files

    def get_files(self):
        return self._files

    def get_file(self):
        return self._files[0]

    def search_files(
            self, rules,
            before_context=0,
            after_context=0,
            parallel=True
    ):
        file2matches = {}
        if parallel:
            with Pool() as pool:
                matches = pool.map(
                        partial(
                            search_in_file_info,
                            rules=rules,
                            before_context=before_context,
                            after_context=after_context
                        ),
                        map(self.cache.get, self._files)
                )
            for matching_rules_by_line, filename in zip(matches, self._files):
                file2matches[filename] = matching_rules_by_line
        else:
            for filename in self._files:
                matching_rules_by_line = self.search_file(
                    filename, rules,
                    before_context, after_context)
                file2matches[filename] = matching_rules_by_line
        return file2matches

