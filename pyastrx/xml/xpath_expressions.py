
from collections import namedtuple

XpathExpressions = namedtuple(
    "XpathExpression",
    ["linenos", "cols_offset"]
)(
    # extract the lineno from the xml element
    "./ancestor-or-self::*[@lineno][1]/@lineno",
    # extract the col_offset from the xml element
    "./ancestor-or-self::*[@col_offset][1]/@col_offset"
)