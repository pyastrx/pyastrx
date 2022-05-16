import os
import json
from rich import print as rprint # noqa
from pyastsearch.search import Repo


def test_print_ast_finds():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    repo = Repo()
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            print(f"\nSearching in {file} for {xpath}")
            repo.load_file(file)
            repo.search_file(file, xpath)


def test_all_code_repo():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    repo = Repo()
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            repo.load_file(file)
            matching_rules_by_line = repo.search_file(file, xpath)
            for lineno, (source_code, rule) in matching_rules_by_line.items():
                assert lineno in linenos


def test_folder_search():
    pyastsearch_folder = os.path.dirname(
        os.path.abspath(__file__)).replace("tests", "pyastsearch")
    repo = Repo()
    repo.load_folder(pyastsearch_folder)
    repo.search_folder(
                "//Name[string-length(@id) > 5]")
