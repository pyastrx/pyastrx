"""This module implements different normalization outputs
for different type inference engines.

"""
from typing import List, cast
from pyastrx.data_typing import PyreType, ASTrXType, MypyType


def pyre2astrx(pyre_types: List[PyreType]) -> List[ASTrXType]:
    """Convert pyre types to astrx types.

    Pyre query returns a list of dicts with the following keys:
    - location: dict with keys "start" and "stop"
    - annotation: str
    The start and stop dicts have keys "line" and "column".

    TODO: This function does nothing. I'll wait until I discover
    how to extract the types from mypy to define a ASTrXType that can be
    easy to interact with both mypy and pyre.

    """
    astrx_types = [cast(ASTrXType, pyre_type) for pyre_type in pyre_types]
    return astrx_types


def mypy2astrx(mypy_types: List[MypyType]) -> List[ASTrXType]:
    """Convert mypy query to astrx types.

    """
    astrx_types = [cast(ASTrXType, mypy_type) for mypy_type in mypy_types]
    return astrx_types
