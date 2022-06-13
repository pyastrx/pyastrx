"""This modules contains dataclasses and aditional
stuff to deal with data typing.

"""
import sys
from dataclasses import dataclass, is_dataclass
import json
from typing import Dict, List, NewType, Tuple, Union, Any, Optional
if sys.version_info[1] < 10:
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

if sys.version_info[1] <= 7:
    from typing_extensions import Literal, TypedDict
else:
    from typing import Literal, TypedDict


from lxml import etree # noqa


class DataClassJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if is_dataclass(obj):
            return obj.__dict__
        return super().default(obj)


AXML: TypeAlias = Union[etree._Element, etree._ElementTree, bytes]


@dataclass
class FileInfo:
    filename: str
    axml: AXML
    txt: str


@dataclass
class RuleInfo:
    name: str = ""
    description: str = ""
    why: str = ""
    severity: str = ""
    use_in_linter: bool = True


RulesDict = NewType('RulesDict', Dict[str, RuleInfo])


@dataclass
class Match:
    cols_by_line: Dict[int, List[int]]
    num_matches: int = 0


Expression2Match = NewType('Expression2Match', Dict[str, Match])


CodeContext = NewType('CodeContext', List[Tuple[int, str]])


@dataclass
class MatchesByLine:
    code_context: CodeContext
    match_by_expr: Expression2Match


@dataclass
class Lines2Matches:
    matches: Dict[int, MatchesByLine]
    num_matches_by_expr: Dict[str, int]


Files2Matches = NewType('Files2Matches', Dict[str, Lines2Matches])


@dataclass
class MatchParams:
    deny_dict: Union[Dict[str, List[str]], None] = None
    allow_dict: Union[Dict[str, List[str]], None] = None


@dataclass
class InferenceConfig:
    what: Literal["pyre", "mypy"] = "pyre"
    run: bool = False


@dataclass
class Config:
    rules: RulesDict
    files: List[str]
    exclude: List[str]
    after_context: int = 1
    before_context: int = 1
    parallel: bool = True
    recursive: bool = True
    interactive: bool = False
    linter: bool = False
    interactive_files: bool = False
    pagination: bool = True
    normalize_ast: bool = True
    vscode_output: bool = False
    quiet: bool = False
    folder: str = "."


class PyreLoc(TypedDict):
    line: int
    column: int


class TokenLoc(TypedDict):
    start: PyreLoc
    stop: PyreLoc


class PyreType(TypedDict):
    location: TokenLoc
    annotation: str


class MypyType(TypedDict):
    location: TokenLoc
    annotation: str
    name: str
    node_name: str
    fullname: Optional[str]
    attrs: List[str]


class PyreFile(TypedDict):
    path: str
    types: List[PyreType]


class MypyInferFileResult(TypedDict):
    path: str
    types: List[MypyType]


class ASTrXType(TypedDict):
    location: TokenLoc
    annotation: str
    name: Optional[str]
    node_name: Optional[str]
    fullname: Optional[str]
    attrs: Optional[List[str]]
