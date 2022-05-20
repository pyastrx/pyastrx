import glob

from pyastrx.ast.things2ast import txt2ast


def test_find_in_ast():
    files = glob.glob('tests/code_repo/*.py.t')
    for filename in files:
        with open(filename, 'r') as f:
            contents = f.read()
        txt2ast(
            contents,
        )