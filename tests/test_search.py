import os
import json
from pyastsearch.search import search_in_folder, search_in_file


def test_print_ast_finds():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            print(f"\nSearching in {file} for {xpath}")
            search_in_file(
                file,
                xpath,
                verbose=False,
                print_xml=False,
                print_matches=False,
            )


def test_all_code_repo():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            matching_lines = search_in_file(
                file,
                xpath,
                verbose=False,
                print_xml=False,
                print_matches=False,
            )
            for expression, info in matching_lines.items():
                for lineno, cols in info["lines"]:
                    assert lineno in linenos


def test_folder_search():
    pyastsearch_folder = os.path.dirname(
        os.path.abspath(__file__)).replace("tests", "pyastsearch")
    search_in_folder(
        pyastsearch_folder,
        "//Name[string-length(@id) > 5]",
        verbose=False,
        print_xml=False,
        print_matches=False,
    )