import glob
from pyastsearch.search import file_contents_to_xml_ast


def test_find_in_ast():
    node_mappings = {}
    files = glob.glob('tests/code_repo/*.py.t')
    for filename in files: 
        with open(filename, 'r') as f:
            contents = f.read()
        xml_ast = file_contents_to_xml_ast(
            contents,
            node_mappings=node_mappings,
        )