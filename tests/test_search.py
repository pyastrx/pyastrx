import json

from pyastrx.search import Repo
from pyastrx.data_typing import RuleInfo, RulesDict, MatchParams


def test_xpath_example_tags():
    """This test using all the keywords in the code_repo/xpath2lineos.json"""

    xpath2linenos = json.load(open("tests/dummy_examples/xpath2linenos.json"))

    for filename, items in xpath2linenos.items():
        file = f"tests/dummy_examples/{filename}"
        for item in items:
            if len(item) == 2:
                xpath, linenos = item
                match_params = {}
            else:
                xpath, linenos, match_params = item
            match_params = MatchParams(**match_params)
            repo = Repo(match_params=match_params)
            repo.load_file(file, normalize_ast=True)
            lines2matches = repo.search_file(
                file, RulesDict({xpath: RuleInfo()}))
            for lineno, _ in lines2matches.items():
                if lineno not in linenos:
                    print(f"{file}:{lineno}")
                    print(linenos)
                    print(xpath)
                    assert False


# def test_evaluator_example_tags():
#     """This test using all the keywords in the code_repo/xpath2lineos.json"""

#     xpath2linenos = json.load(open("tests/dummy_examples/xpath2linenos.json"))
#     repo = Repo()
#     for filename, items in xpath2linenos.items():
#         file = f"tests/dummy_examples/{filename}"
#         rules = RulesDict({xpath: RuleInfo() for xpath, _ in items})
#         repo.load_file(file, normalize_ast=True)
#         lines2matches = repo.search_file(file, rules)