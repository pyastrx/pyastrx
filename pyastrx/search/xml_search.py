from lxml import etree

from pyastrx.xml.xpath_expressions import XpathExpressions
from pyastrx.xml.xpath_extensions import lxml_ext_pyastrx, lxml_ext_regex

# initialize the extension functions
lxml_ext_regex.prefix = "re"
lxml_ext_pyastrx.prefix = "pyastrx"


def get_xml_el_value(element, xpath_name):
    xpath_expr = getattr(XpathExpressions, xpath_name)
    try:
        return element.xpath(xpath_expr)
    except AttributeError:
        return None


def linenos_from_xml(elements):
    """Given a list of elements, return a list of line numbers."""
    lines = {}
    for element in elements:
        linenos = get_xml_el_value(element, "linenos")
        cols_offset = get_xml_el_value(element, "cols_offset")

        if linenos:
            col = int(cols_offset[0]) if cols_offset else 0
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
            "num_matches": len(matching_lines_by_exp)
        }
    return matching_by_expression
