from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import List, Union, Optional


from pyastrx.inference.pyre import infer_types as infer_types_pyre
from pyastrx.inference.mypy import infer_types as infer_types_mypy
from pyastrx.inference.normalization import pyre2astrx, mypy2astrx
from pyastrx.ast.ast2xml import file2axml
from pyastrx.data_typing import (Files2Matches, Lines2Matches, MatchParams,
                                 RulesDict, ASTrXType, InferenceConfig)
from pyastrx.search.cache import Cache
from pyastrx.search.xml_search import search_in_file_info


class Repo:
    def __init__(
            self, match_params: MatchParams,
            inference: Optional[InferenceConfig] = None,
            file_cache: bool = True,
    ) -> None:
        self.cache = Cache(file_cache)
        self._files: List[str] = []
        if match_params is None:
            match_params = {}
        self.match_params = match_params
        self.inference = inference

    def load_file(
            self, filename: str, normalize_ast: bool,
            infered_types: Optional[List[ASTrXType]] = None) -> None:
        """
        Args:

        """
        should_update = self.cache.update(filename)
        self._files = [filename]
        if should_update:
            info = file2axml(
                filename=filename, normalize_ast=normalize_ast,
                infered_types=infered_types, baxml=True)
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
            files_path = Path(folder).rglob(f"*.{extension}")
        else:
            files_path = Path(folder).glob(f"*.{extension}")
        files = [
            str(f.resolve()) for f in files_path
            if not any(d in f.parts for d in exclude)
        ]
        self.load_files(
            files, parallel, normalize_ast)

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
            if self.cache.update(filename)
        ]
        if len(files2load) == 0:
            self._files = files
            return

        use_infered_types = False
        inference_result: List[List[ASTrXType]]
        if self.inference and self.inference.run:
            if self.inference.what == "pyre":
                inference_result_pyre, use_infered_types = infer_types_pyre(
                    files2load)
                if use_infered_types:
                    inference_result = [
                        pyre2astrx(infered_types["types"])
                        for infered_types in inference_result_pyre
                    ]
            elif self.inference.what == "mypy":
                inference_result_mypy, use_infered_types = infer_types_mypy(
                    files2load)
                if use_infered_types:
                    inference_result = [
                        mypy2astrx(infered_types["types"])
                        for infered_types in inference_result_mypy
                    ]
        files_and_types = [
            (filename, inference_result[i])
            if use_infered_types else (filename, None)
            for i, filename in enumerate(files2load)
        ]

        if parallel:
            with Pool() as pool:
                infos = pool.starmap(
                    partial(
                        file2axml,
                        normalize_ast=normalize_ast,
                        baxml=True
                    ),
                    files_and_types
                )
            for info, filename in zip(infos, files2load):
                if info is None:
                    raise Exception(f"Failed to convert {filename}")
                self.cache.set(filename, info)

            self._files = files
            return

        for filename, infered_types in files_and_types:
            self.load_file(
                filename, normalize_ast=normalize_ast,
                infered_types=infered_types)
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
