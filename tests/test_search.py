import json
import os

from pyastrx.search import Repo
from pyastrx.data_typing import RuleInfo, RulesDict


def test_xpath_example_tags():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/code_repo/xpath2linenos.json"))
    repo = Repo()
    for filename, items in xpath2linenos.items():
        file = f"tests/code_repo/{filename}"
        for (xpath, linenos) in items:
            repo.load_file(file, normalize_ast=True)
            lines2matches = repo.search_file(file, RulesDict({xpath: RuleInfo()}))
            for lineno, _ in lines2matches.items():
                if not lineno in linenos:
                    print(f"{file}:{lineno}")
                    print(linenos)
                    print(xpath)
                    assert False