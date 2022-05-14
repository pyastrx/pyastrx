import os
import json
from pyastsearch.search import search


def test_print_ast_finds():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""
    
    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:       
            print(f"Searching in {file} for {xpath}") 
            files2linenos = search(
                file,
                xpath,
                verbose=False,
                recurse=False,
                print_xml=False,
                print_matches=True,
            )


def test_all_code_repo():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""
    
    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            files2linenos = search(
                file,
                xpath,
                verbose=False,
                recurse=False,
                print_xml=False,
                print_matches=False,
            )
            for file, linenos_search in files2linenos.items():
                for lineno in linenos_search:
                    assert lineno in linenos
    

def test_folder_search():
    pyastsearch_folder = os.path.dirname(
        os.path.abspath(__file__)).replace("tests", "pyastsearch")
    search(
        pyastsearch_folder,
        "//Name[string-length(@id) > 5]",
        verbose=False,
        print_xml=False,
        print_matches=True,
    )