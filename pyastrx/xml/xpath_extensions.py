"""All the xpath extensions should be defined here."""
import re
from typing import List

from lxml import etree

regexp_url = "https://pyastrx.readthedocs.io/regex"
lxml_ext_regex = etree.FunctionNamespace(regexp_url)

pyastrx_url = "https://pyastrx.readthedocs.io/pyastrx"
lxml_ext_pyastrx = etree.FunctionNamespace(pyastrx_url)


@lxml_ext_pyastrx
def anyin(context, values_check: List, values: List) -> bool:
    print(f"anyin: {values_check} in {values}")
    """Allows to check if the results of a xpath are inside
    of a list of another xpath results.

    Args:
        context: lxml.etree._XPathContext
        values_check: list of values to check
        values: list of values to check against
    Returns:
        bool: True if the values are inside of the values_check

    """

    for value in values:
        if value in values_check:
            return True
    return False


@lxml_ext_regex
def match(context, pattern, strings):
    for s in strings:
        if re.match(pattern, s) is not None:
            return True
    return False


@lxml_ext_regex
def search(context, pattern, strings):
    for s in strings:
        if re.search(pattern, s) is not None:
            return True
    return False

