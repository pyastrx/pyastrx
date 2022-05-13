import os
from pyastsearch.search import search


def test_folder_search():
    pyastsearch_folder = os.path.dirname(
        os.path.abspath(__file__)).replace("tests", "pyastsearch")
    print(pyastsearch_folder)
    search(
        pyastsearch_folder,
        "//Name[string-length(@id) > 5]",
        verbose=False,
        print_xml=False,
        print_matches=True,
    )