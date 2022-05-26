import copyreg
from functools import partial
from io import BytesIO
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, List, Tuple, Union

from lxml import etree

from pyastrx.ast.ast2xml import file2axml
from pyastrx.data_typing import (
    Files2Matches, Lines2Matches, RulesDict, MatchParams)
from pyastrx.search.cache import Cache
from pyastrx.search.xml_search import search_in_file_info


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


class Repo:
    def __init__(self, match_params: MatchParams) -> None:
        self.cache = Cache()
        self._files: List[str] = []
        if match_params is None:
            match_params = {}
        self.match_params = match_params

    def load_file(
            self, filename: str, normalize_ast: bool) -> None:
        should_update, _ = self.cache.update(filename)
        self._files = [filename]
        if should_update:
            info = file2axml(filename, normalize_ast)
            self.cache.set(filename, info)

    def search_file(
            self, filename: str, rules: RulesDict,
            before_context: int = 0,
            after_context: int = 0) -> Lines2Matches:
        info = self.cache.get(filename)
        matching_by_line = search_in_file_info(
            info, rules, before_context, after_context, self.match_params)

        return matching_by_line

    def load_folder(
        self,
        folder: str,
        normalize_ast: bool,
        recursive: bool = True,
        parallel: bool = True,
        extension: str = "py",
        exclude: Union[List[str], None] = None,
    ) -> None:
        if exclude is None:
            exclude = [".venv", ".tox"]
        if recursive:
            files = Path(folder).rglob(f"*.{extension}")
        else:
            files = Path(folder).glob(f"*.{extension}")
        files = [
            str(f.resolve()) for f in files
            if not any(d in f.parts for d in exclude)
        ]
        self.load_files(files, parallel, normalize_ast)

    def load_files(
        self,
        files: List[str],
        parallel: bool,
        normalize_ast: bool,
    ) -> None:

        files = [
            str(Path(file).resolve()) for file in files]
        files2load = [
            filename for filename in files
            if self.cache.update(filename)[0] is True
        ]
        if len(files2load) == 0:
            return

        if parallel:
            with Pool() as pool:
                infos = pool.map(
                        partial(
                            file2axml, normalize_ast=normalize_ast),
                        files2load)
            for info, filename in zip(infos, files2load):
                if info is None:
                    raise Exception(f"Failed to convert {filename}")
                self.cache.set(filename, info)
        else:
            for filename in files2load:
                self.load_file(filename, normalize_ast=normalize_ast)

        self._files = files

    def get_files(self) -> List[str]:
        return self._files

    def get_file(self) -> str:
        return self._files[0]

    def search_files(
            self, rules: RulesDict,
            before_context: int = 0,
            after_context: int = 0,
            parallel: bool = True
    ) -> Files2Matches:

        file2matches = {}
        if parallel:
            with Pool() as pool:
                matches_by_file = pool.map(
                        partial(
                            search_in_file_info,
                            rules=rules,
                            before_context=before_context,
                            after_context=after_context,
                            match_params=self.match_params
                        ),
                        map(self.cache.get, self._files)
                )
            for filename, matches_by_line in zip(self._files, matches_by_file):
                file2matches[filename] = matches_by_line

        else:
            for filename in self._files:
                match_by_lines = self.search_file(
                    filename, rules,
                    before_context, after_context)
                file2matches[filename] = match_by_lines
        return Files2Matches(file2matches)

