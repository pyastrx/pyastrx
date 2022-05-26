from typing import Dict, List, Tuple

from lxml import etree

from pyastrx.data_typing import (Expression2Match, FileInfo, Lines2Matches,
                                 Match, MatchesByLine, RulesDict, MatchParams)
from pyastrx.search.txt_tools import apply_context
from pyastrx.xml.xpath_expressions import XpathExpressions
from pyastrx.xml.xpath_extensions import (
    LXMLExtensions, __all_lxml_ext__, __lxml_namespaces__)


def get_xml_el_value(
        element: etree._Element,
        xpath_name: str) -> Tuple[List[int], bool]:
    xpath_expr = getattr(XpathExpressions, xpath_name)
    try:
        result = [int(r) for r in element.xpath(xpath_expr)]
        return result, True
    except AttributeError:
        return [0], False


def linenos_from_xml(
        elements: List[etree._Element]) -> Dict[int, List[int]]:
    """Given a list of elements, return a list of line numbers."""
    lines: Dict[int, List[int]] = {}
    for element in elements:
        linenos, success_line = get_xml_el_value(element, "linenos")
        cols_offset, _ = get_xml_el_value(element, "cols_offset")

        if success_line:
            col = cols_offset[0]
            line_num = linenos[0]

            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(col)

    return lines


def search_in_axml(
        rules: RulesDict, axml: etree._Element) -> Expression2Match:
    matching_by_expression = Expression2Match({})
    for expression, rule_info in rules.items():
        try:
            matching_elements = axml.xpath(expression)
            cols_by_line = linenos_from_xml(
                matching_elements)
            matching_by_expression[expression] = Match(
                cols_by_line,
                rule_info,
                len(cols_by_line)
            )
        except etree.XPathEvalError:
            print(f"XPath error: {expression}")

    return matching_by_expression


def search_evaluator(
        rules: RulesDict, evaluator: etree.XPathEvaluator) -> Expression2Match:
    matching_by_expression = Expression2Match({})
    for expression, rule_info in rules.items():
        try:
            matching_elements = evaluator(expression)
            cols_by_line = linenos_from_xml(
                matching_elements)
            matching_by_expression[expression] = Match(
                cols_by_line,
                rule_info,
                len(cols_by_line)
            )
        except etree.XPathEvalError:
            print(f"XPath error: {expression}")

    return matching_by_expression


def search_in_file_info(
        file_info: FileInfo, rules: RulesDict,
        before_context: int = 0, after_context: int = 0,
        match_params: MatchParams = None,
        use_evaluator: bool = True) -> Lines2Matches:
    if file_info is None:
        return {}
    if use_evaluator:
        if match_params is None:
            match_params = MatchParams({})
        extension_module = LXMLExtensions(**match_params.__dict__)
        extensions = etree.Extension(
            extension_module, __all_lxml_ext__, ns='local-ns')
        evaluator = etree.XPathEvaluator(
            file_info.axml,
            namespaces=__lxml_namespaces__, extensions=extensions
        )
        matching_by_expression = search_evaluator(
            rules,
            evaluator)
    else:
        matching_by_expression = search_in_axml(
                rules,
                axml=file_info.axml)
    match_expr_by_line = {}
    for expression, match in matching_by_expression.items():
        for line_num, cols in match.cols_by_line.items():
            if line_num not in match_expr_by_line:
                code_context = apply_context(
                    file_info.txt.splitlines(), line_num - 1,
                    before_context, after_context)
                match_expr_by_line[line_num] = MatchesByLine(code_context, {})
            match_expr_by_line[line_num].match_by_expr[expression] = Match(
                {line_num: cols}, match.rule_info, match.num_matches
            )
    return Lines2Matches(match_expr_by_line)
