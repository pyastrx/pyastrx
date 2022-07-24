from typing import Dict, List, Tuple, Optional, Union
from io import BytesIO
from lxml import etree

from pyastrx.data_typing import (Expression2Match, FileInfo, Lines2Matches,
                                 Match, MatchesByLine, MatchParams, RulesDict)
from pyastrx.search.txt_tools import apply_context
from pyastrx.xml.xpath_expressions import XpathExpressions
from pyastrx.xml.xpath_extensions import (LXMLExtensions, __all_lxml_ext__,
                                          __lxml_namespaces__)


def get_xml_el_value(
        element: etree._Element,
        xpath_name: str) -> Tuple[List[int], bool]:
    xpath_expr = getattr(XpathExpressions, xpath_name)
    xml_result = element.xpath(xpath_expr)
    if isinstance(xml_result, list):
        result: List[int] = []
        for r in xml_result:
            if (
                isinstance(r, float)
                or isinstance(r, str)
                or isinstance(r, int)
            ):
                result.append(int(r))
        return result, True
    else:
        return [0], False


def linenos_from_xml(
        element: etree._Element) -> Tuple[List[int], List[int], bool]:
    linenos, success_line = get_xml_el_value(element, "linenos")
    cols_offset, success_col = get_xml_el_value(element, "cols_offset")
    success = success_line and success_col
    return linenos, cols_offset, success


def search_evaluator(
        rules: RulesDict,
        evaluator: etree.XPathElementEvaluator) -> Expression2Match:
    matching_by_expression = Expression2Match({})
    for expression, _ in rules.items():
        try:
            matching_elements = evaluator(expression)
        except etree.XPathEvalError:
            continue
        if not isinstance(matching_elements, list):
            continue
        line2cols: Dict[int, List[int]] = {}
        for element in matching_elements:
            if not isinstance(element, etree._Element):
                continue
            linenos, cols, success = linenos_from_xml(
                element)
            if not success or len(linenos) == 0:
                continue
            col = cols[0]
            line_num = linenos[0]
            if line_num not in line2cols:
                line2cols[line_num] = []
            line2cols[line_num].append(col)

        matching_by_expression[expression] = Match(
            line2cols,
            len(line2cols)
        )

    return matching_by_expression


def search_in_file_info(
        file_info: FileInfo, rules: RulesDict,
        before_context: int, after_context: int,
        match_params: Optional[MatchParams]) -> Lines2Matches:

    extension_module = LXMLExtensions(**match_params.__dict__)
    extensions = etree.Extension(
        extension_module, __all_lxml_ext__, ns='local-ns')
    axml: Union[etree._Element, etree._ElementTree]
    if isinstance(file_info.axml, bytes):
        axml = etree.parse(BytesIO(file_info.axml))
    else:
        axml = file_info.axml
    evaluator = etree.XPathEvaluator(
        axml,
        namespaces=__lxml_namespaces__, extensions=extensions
    )
    matching_by_expr = search_evaluator(
        rules,
        evaluator)

    match_expr_by_line = {}
    expr2num = {}
    for expr, match in matching_by_expr.items():
        for line_num, cols in match.cols_by_line.items():
            if line_num not in match_expr_by_line:
                code_context = apply_context(
                    file_info.txt.splitlines(), line_num - 1,
                    before_context, after_context)
                match_expr_by_line[line_num] = MatchesByLine(
                    code_context, Expression2Match({}))
            match_expr_by_line[line_num].match_by_expr[expr] = Match(
                {line_num: cols}, match.num_matches
            )
            expr2num[expr] = match.num_matches
            expr2num[expr] = expr2num.get(expr, 0) + match.num_matches

    return Lines2Matches(match_expr_by_line, expr2num)
