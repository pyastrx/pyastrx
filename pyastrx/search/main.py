from typing import Tuple, Callable
from pathlib import Path
from io import BytesIO
import copyreg
from multiprocessing import Pool

from lxml import etree
from pyastrx.search.cache import Cache
from pyastrx.search.code2axml import file2axml
from pyastrx.search.xml_search import search_in_axml
from pyastrx.search.txt_tools import apply_context


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


class Repo:
    def __init__(self):
        self._cache = Cache()
        self._cache.load()

    def load_file(self, filename):
        info, _ = self._cache.update(filename)
        self._files = [filename]
        if not info:
            info = file2axml(filename)
            self._cache.set(filename, info)

    def search_file(
            self, filename, rules,
            with_txt=True,
            before_context=0,
            after_context=0):
        info = self._cache.get(filename)
        if info is None:
            print(f"{filename} not found in cache")
            return {}
        matching_lines_by_rule = search_in_axml(
            rules,
            axml=info.axml,
            node_mappings=info.node_mappings)
        matching_rules_by_line = {}
        if with_txt:
            for expression, matching_lines in matching_lines_by_rule.items():
                line_nums = matching_lines["line_nums"]
                for line_num, cols in line_nums:
                    if line_num not in matching_rules_by_line:
                        matching_lines_context = apply_context(
                            info.txt.splitlines(), line_num - 1,
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
            if self._cache.update(filename)[0] is False
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
                self._cache.set(filename, info)
        else:
            for filename in files2load:
                self.load_file(filename)

        self._files = files

    def search_folder(
            self, rules,
            with_txt=True,
            before_context=0,
            after_context=0,
    ):
        file2matches = {}
        for filename in self._files:
            matching_rules_by_line = self.search_file(
                filename, rules, with_txt,
                before_context, after_context)
            file2matches[filename] = matching_rules_by_line
        return file2matches

