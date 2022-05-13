import re
from lxml.etree import tostring
from lxml import etree

class XMLVersions:
    LXML = object()
    XML = object()
XML_VERSION = XMLVersions.LXML


def _query_factory(verbose=False):
    def lxml_query(element, expression):
        return element.xpath(expression)

    def xml_query(element, expression):
        return element.findall(expression)

    if XML_VERSION is XMLVersions.LXML:
        return lxml_query
    else:
        if verbose:
            print(
                "WARNING: lxml could not be imported, "
                "falling back to native XPath engine."
            )
        return xml_query


def _tostring_factory():
    def xml_tostring(*args, **kwargs):
        kwargs.pop('pretty_print')
        return tostring(*args, **kwargs)

    if XML_VERSION is XMLVersions.LXML:
        return tostring
    else:
        return xml_tostring


if XML_VERSION is XMLVersions.LXML:
    regex_ns = etree.FunctionNamespace('https://github.com/hchasestevens/astpath')
    regex_ns.prefix = 're'

    @regex_ns
    def match(ctx, pattern, strings):
        return any(
            re.match(pattern, s) is not None
            for s in strings
        )

    @regex_ns
    def search(ctx, pattern, strings):
        return any(
            re.search(pattern, s) is not None
            for s in strings
        )