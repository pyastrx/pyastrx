from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional, Literal
from dataclasses import asdict


from pyastrx.inference.pyre import infer_types as infer_types_pyre
from pyastrx.inference.mypy import infer_types as infer_types_mypy
from pyastrx.inference.normalization import pyre2astrx, mypy2astrx
from pyastrx.axml.python.ast2xml import file2axml
from pyastrx.axml.yaml.yaml2xml import file2axml as yaml2axml
from pyastrx.data_typing import (
    Files2Matches,
    Lines2Matches,
    MatchParams,
    FileInfo,
    RulesDict,
    ASTrXType,
    InferenceConfig,
    Specifications,
    Specification,
)
from pyastrx.search.cache import Cache
from pyastrx.search.xml_search import search_in_file_info


class Repo:
    def __init__(
        self,
        match_params: MatchParams,
        inference: Optional[InferenceConfig] = None,
        file_cache: bool = True,
    ) -> None:
        self.cache = Cache(file_cache)
        self._files: List[str] = []
        if match_params is None:
            match_params = {}
        self.match_params = match_params
        self.inference = inference

    def search_file(
        self,
        filename: str,
        rules: RulesDict,
        before_context: int = 0,
        after_context: int = 0,
    ) -> Lines2Matches:
        info = self.cache.get(filename)
        matching_by_line = search_in_file_info(
            info, rules, before_context, after_context, self.match_params
        )
        return matching_by_line

    def load_file(
        self,
        filename: str,
        specification_name: str,
        language: Literal["python", "yaml"] = "python",
        normalize_ast: bool = True,
        infered_types: Optional[List[ASTrXType]] = None,
    ) -> FileInfo:
        """
        Args:

        """
        should_update = self.cache.update(filename)
        self._files = [filename]
        if not should_update:
            return self.cache.get(filename)
        if language == "python":
            info = file2axml(
                filename=filename,
                specification_name=specification_name,
                normalize_ast=normalize_ast,
                infered_types=infered_types,
                baxml=True,
            )
            self.cache.set(filename, info)
        elif language == "yaml":
            info = yaml2axml(
                filename=filename,
                baxml=True, specification_name=specification_name
            )
            self.cache.set(filename, info)
        return info

    def load_python_files(
        self,
        files2load: List[str],
        specification_name: str,
        parallel: bool = True,
        normalize_ast: bool = True,
        **kwargs,
    ) -> None:

        use_infered_types = False
        inference_result: List[List[ASTrXType]]
        if self.inference and self.inference.run:
            if self.inference.what == "pyre":
                inference_result_pyre, use_infered_types = infer_types_pyre(files2load) # noqa
                if use_infered_types:
                    inference_result = [
                        pyre2astrx(infered_types["types"])
                        for infered_types in inference_result_pyre
                    ]
            elif self.inference.what == "mypy":
                inference_result_mypy, use_infered_types = infer_types_mypy(files2load) # noqa
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
                        specification_name=specification_name,
                        normalize_ast=normalize_ast,
                        baxml=True,
                    ),
                    files_and_types,
                )
        else:
            infos = [
                self.load_file(
                    filename,
                    specification_name=specification_name,
                    normalize_ast=normalize_ast,
                    language="python",
                    infered_types=infered_types,
                )
                for filename, infered_types in files_and_types
            ]

        for info, filename in zip(infos, files2load):
            if info is None:
                raise Exception(f"Failed to convert {filename}")
            self.cache.set(filename, info)

    def load_yaml_files(
        self, files2load: List[str],
        specification_name: str, parallel: bool, **kwargs
    ) -> None:
        parallel = False
        if parallel:
            with Pool() as pool:
                infos = pool.map(
                    partial(
                        yaml2axml,
                        specification_name=specification_name, baxml=True
                    ),
                    files2load,
                )
        else:
            infos = [
                self.load_file(
                    filename,
                    specification_name=specification_name, language="yaml"
                )
                for filename in files2load
            ]
        for info, filename in zip(infos, files2load):
            if info is None:
                raise Exception(f"Failed to convert {filename}")
            self.cache.set(filename, info)

    def load_files(
        self,
        files: List[str],
        specification_name: str,
        language: Literal["python", "yaml"] = "python",
        **kwargs,
    ) -> None:

        files = [str(Path(file).resolve()) for file in files]
        files2load = [
            filename for filename in files if self.cache.update(filename)]
        if len(files2load) == 0:
            self._files.extend(files)
            return

        if language == "python":
            self.load_python_files(
                files2load, specification_name=specification_name, **kwargs
            )
        elif language == "yaml":
            self.load_yaml_files(
                files2load, specification_name=specification_name, **kwargs
            )

        self._files.extend(files)

    def load_folder(
        self,
        specification_name: str,
        specification: Specification,
    ) -> None:
        files_path: List[Path] = []
        path_obj = Path(specification.folder)
        for ext in specification.extensions:
            method = "glob"
            if specification.recursive:
                method = "rglob"

            files_path.extend([
                f
                for f in getattr(path_obj, method)(f"*{ext}")
                if f.is_file()
            ])

        files = [
            str(f.resolve())
            for f in files_path
            if not any(d in f.parts for d in specification.exclude)
        ]
        specs_dict = asdict(specification)
        del specs_dict["files"]
        self.load_files(
            files,
            specification_name,
            **specs_dict,
        )

    def load_specification(
        self, specification_name: str, specification: Specification
    ) -> None:
        files = specification.files
        if len(files) > 0:
            self.load_files(
                specification_name=specification_name, **asdict(specification)
            )
            return

        self.load_folder(
            specification_name=specification_name, specification=specification
        )

    def load_specifications(self, specifications: Specifications) -> None:
        for spec in specifications:
            self.load_specification(spec, specifications[spec])

    def get_files(self) -> List[str]:
        return self._files

    def get_file(self) -> str:
        files = self.get_files()
        if len(files) == 0:
            print(
                "[\033[91mERROR\033[0m]",
                "No files to search in. Check your PyASTrX specifications.",
            )
            exit(1)
        return files[0]

    def search_files(
        self,
        rules: RulesDict,
        before_context: int = 0,
        after_context: int = 0,
        parallel: bool = True,
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
                        match_params=self.match_params,
                    ),
                    map(self.cache.get, self._files),
                )
            for filename, matches_by_line in zip(self._files, matches_by_file):
                file2matches[filename] = matches_by_line

        else:
            for filename in self._files:
                match_by_lines = self.search_file(
                    filename, rules, before_context, after_context
                )
                file2matches[filename] = match_by_lines
        return Files2Matches(file2matches)
