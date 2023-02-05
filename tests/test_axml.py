from functools import partial
from pyastrx.axml.python.ast2xml import set_encoded_literal
from pyastrx.axml.yaml.yaml2xml import txt2axml


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


def test_txt2axml_simple():
    test_string = "test: 1"
    xml_yaml = txt2axml(test_string)
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


def test_txt2axml_bad_yaml():
    txt_invalid_yaml = "test: 1\n  test2: 2"
    xml_yaml = txt2axml(txt_invalid_yaml)
    assert xml_yaml.tag == "Module"
    assert len(xml_yaml) == 0
