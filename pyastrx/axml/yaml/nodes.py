from lxml import etree


def check_type(value):
    try:
        int(value)
        return 'Int'
    except ValueError:
        pass
    try:
        float(value)
        return 'Float'
    except ValueError:
        pass
    if value == 'true' or value == 'false':
        return 'Bool'
    return 'Str'


class Node(object):
    def __init__(self, tag, value, start_mark, end_mark):
        self.tag = tag
        self.value = value
        self.start_mark = start_mark
        self.end_mark = end_mark

    def get_xml_node(
        self, key_node=False, module_node=False, file_path=None
    ) -> etree._Element:
        """Return the XML node for the YAML node.

        Will recursively call itself to build the string representation
        using the lxml

        """

        class_name = self.__class__.__name__
        set_key_node = False
        tag = self.tag
        lineno = self.start_mark.line + 1
        end_lineno = self.end_mark.line + 1
        col_offset = self.start_mark.column
        end_col_offset = self.end_mark.column
        value = self.value
        xml_node = etree.Element(class_name)
        if module_node:
            xml_node.tag = "Module"
            xml_node.set("file_path", file_path)
        if key_node and class_name == 'ScalarNode':
            if isinstance(self.value, str):
                set_key_node = True
                xml_node.tag = "KeyNode"
                xml_node.set("name", self.value)

        if tag is not None:
            xml_node.set("tag", tag)
        xml_node.set("lineno", str(lineno))
        xml_node.set("end_lineno", str(end_lineno))
        xml_node.set("col_offset", str(col_offset))
        xml_node.set("end_col_offset", str(end_col_offset))
        if isinstance(value, str):
            if set_key_node:
                return xml_node

            xml_node.tag = f"{check_type(value)}Node"
            xml_node.text = value
            return xml_node

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    xml_node.text = item
                    return xml_node
                elif isinstance(item, Node):
                    xml_node.append(item.get_xml_node())
                elif isinstance(item, tuple):
                    assert len(item) == 2
                    node_key = item[0].get_xml_node(key_node=True)
                    node_value = item[1].get_xml_node()
                    node_key.append(node_value)
                    xml_node.append(node_key)
                else:
                    raise ValueError("Unexpected type: %s" % type(item))
            return xml_node
        elif isinstance(value, Node):
            xml_node.append(value.get_xml_node())
            return xml_node

        raise ValueError("Unexpected type: %s" % type(value))

    def __repr__(self):
        value = self.value
        value = repr(value)
        return f"{self.__class__.__name__}(tag={self.tag}, value={value})"


class ScalarNode(Node):
    id = 'scalar'

    def __init__(
            self, tag, value,
            start_mark=None, end_mark=None, style=None):
        self.tag = tag
        self.value = value
        self.start_mark = start_mark
        self.end_mark = end_mark
        self.style = style


class CollectionNode(Node):
    def __init__(
            self, tag, value,
            start_mark=None, end_mark=None, flow_style=None):
        self.tag = tag
        self.value = value
        self.start_mark = start_mark
        self.end_mark = end_mark
        self.flow_style = flow_style


class SequenceNode(CollectionNode):
    id = 'sequence'


class MappingNode(CollectionNode):
    id = 'mapping'
