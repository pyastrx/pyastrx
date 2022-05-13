from pyastsearch.search import search


def test_re_search():
    file = "tests/code_repo/custom_re_xpath.py"
    xpath = "//ClassDef[re:match('.*Var', @name)]"
    search(
        file,
        xpath,
        verbose=False,
        recurse=False,
        print_xml=False,
        print_matches=True,
    )
    