from functools import partial

import gast
from pyastrx.axml.python.ast2xml import set_encoded_literal, txt2ast
from pyastrx.axml.yaml.yaml2xml import txt2axml as yamlTxt2axml


def create_test_obj():
    test_obj = type("TestObj", (object,), {})()
    test_obj.test_attr = None
    return test_obj


def test_set_encoded_literal():
    test_number = 1
    test_string = "1"
    test_float = 1.0
    test_string_float = "1.0"
    test_bytes = b"1.0"
    # creat a test_object with tetst_attr
    test_obj = create_test_obj()
    set_encoded_literal(partial(test_obj.__setattr__, "test_attr"), test_number)
    assert test_obj.test_attr == b"1"
    set_encoded_literal(partial(test_obj.__setattr__, "test_attr"), test_string)
    assert test_obj.test_attr == b"1"
    set_encoded_literal(partial(test_obj.__setattr__, "test_attr"), test_float)
    assert test_obj.test_attr == b"1.0"
    set_encoded_literal(partial(test_obj.__setattr__, "test_attr"), test_string_float)
    assert test_obj.test_attr == b"1.0"
    set_encoded_literal(partial(test_obj.__setattr__, "test_attr"), test_bytes)
    assert test_obj.test_attr == ""


def test_yaml_txt2axml_simple():
    test_string = "test: 1"
    xml_yaml = yamlTxt2axml(test_string)
    assert xml_yaml.tag == "Module"
    first_node = xml_yaml[0]
    assert first_node.tag == "KeyNode"
    for attr, value in (
        ("name", "test"),
        ("lineno", "1"),
        ("col_offset", "0"),
        ("end_lineno", "1"),
        ("end_col_offset", "4"),
    ):
        assert first_node.attrib[attr] == value
    int_node = first_node[0]
    assert int_node.tag == "IntNode"

    for attr, value in (
        ("lineno", "1"),
        ("col_offset", "6"),
        ("end_lineno", "1"),
        ("end_col_offset", "7"),
    ):
        assert int_node.attrib[attr] == value
    assert int_node.text == "1"


def test_fix_py_and_parse():
    txt_inv = "def test(a=[1,2,3]):\n\treturn a[0]\ntest()\ndef ()\n"

    txt_fix = "def test(a=[1,2,3]):\n\treturn a[0]\ntest()"
    gast_ast = txt2ast(txt_inv)
    gast_ast_fix = gast.parse(txt_fix)
    code_str = gast.unparse(gast_ast)
    code_str_fix = gast.unparse(gast_ast_fix)

    assert code_str == code_str_fix


def test_txt2axml_bad_yaml():
    txt_invalid_yaml = "test: 1\n  test2: 2"
    xml_yaml = yamlTxt2axml(txt_invalid_yaml)
    assert xml_yaml.tag == "Module"
    assert len(xml_yaml) == 0


def test_fix_yaml_and_parse():
    txt_inv = "test:1\ntest2:2\n test: sdfatest: 1\ntest2: 2"
    txt_fix = "test:1\ntest2:2"
    xml_fix = yamlTxt2axml(txt_inv)
    xml_inv = yamlTxt2axml(txt_fix)
    assert xml_fix.tag == xml_inv.tag
    assert len(xml_fix) == len(xml_inv)
    for i in range(len(xml_fix)):
        assert xml_fix[i].tag == xml_inv[i].tag
        assert xml_fix[i].attrib == xml_inv[i].attrib
        assert xml_fix[i].text == xml_inv[i].text
