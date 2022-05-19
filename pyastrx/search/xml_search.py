from lxml import etree
from pyastrx.search.xml.xpath_extensions import (
    lxml_ext_pyastrx, lxml_ext_regex)


# initialize the extension functions
lxml_ext_regex.prefix = "re"
lxml_ext_pyastrx.prefix = "pyastrx"


def linenos_from_xml(elements):
    """Given a list of elements, return a list of line numbers."""
    lines = {}
    for element in elements:
        try:
            linenos = element.xpath("./ancestor-or-self::*[@lineno][1]/@lineno")
            col_offset = element.xpath("./ancestor-or-self::*[@col_offset][1]/@col_offset")
        except AttributeError:
            raise AttributeError("Element has no ancestor with line number.")

        if linenos:
            col = int(col_offset[0]) if col_offset else 0
            linenos = int(linenos[0])

            if linenos not in lines:
                lines[linenos] = [linenos, [col]]
            else:
                lines[linenos][1].append(col)

    lines = list(lines.values())
    return lines


def search_in_axml(rules, axml):
    matching_by_expression = {}
    if isinstance(rules, str):
        rules = {rules: {}}
    elif isinstance(rules, list):
        rules = {rule: {} for rule in rules}
    for expression, rule in rules.items():
        try:
            matching_elements = axml.xpath(expression)
            matching_lines_by_exp = linenos_from_xml(
                matching_elements)
        except etree.XPathEvalError:
            print(f"XPath error: {expression}")
            matching_lines_by_exp = []
            rule = {}

        matching_by_expression[expression] = {
            "line_nums": matching_lines_by_exp,
            "rule_infos": rule,
        }
    return matching_by_expression