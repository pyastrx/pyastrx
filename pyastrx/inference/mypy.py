from pathlib import Path
from typing import List, Tuple

import mypy.main as MAIN
import mypy.build as BUILD
from mypy.nodes import MypyFile as MypyFileType

from pyastrx.data_typing import MypyInferFileResult
from pyastrx.inference.mypy_visitor import TypeExtractor


def infer_types(
        files: List[str], ) -> Tuple[List[MypyInferFileResult], bool]:

    mfiles, opt = MAIN.process_options(
        files,
    )
    opt.preserve_asts = True
    opt.fine_grained_incremental = True
    opt.use_fine_grained_cache = True
    result = BUILD.build(
        mfiles, options=opt,
    )

    mypy_query: List[MypyInferFileResult] = []
    base_folder = str(Path(".").resolve()) + "/"
    for file in files:
        mod = file.replace(base_folder, "").replace("/", ".")
        mod = mod.replace(".py", "")
        mypy_query.append({
            "path": file,
            "types": []
        })
        types_info = []
        if mod not in result.graph:
            continue
        tree = result.graph[mod].tree
        if not isinstance(tree, MypyFileType):
            continue
        visitor = TypeExtractor(tree)
        visitor.visit_mypy_file(tree)
        types_info = visitor.types_info
        mypy_query[-1]["types"] = types_info

    return mypy_query, True
