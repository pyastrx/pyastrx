from typing import Any, List, Tuple, Union
from typing_extensions import TYPE_CHECKING

import mypy.nodes

from mypy.traverser import TraverserVisitor

from pyastrx.data_typing import MypyType, TokenLoc

if TYPE_CHECKING: # noqa:
    import mypy.patterns # noqa:


class TypeExtractor(TraverserVisitor):
    """Visitor for converting a mst node into a dictonary
    with the type information and other useful information

    """

    def __init__(self, tree: 'mypy.nodes.MypyFile') -> None:
        self.types_info: List[MypyType] = []
        self.tree = tree

    def navigate_func_def(self, o: 'mypy.nodes.FuncDef') -> None:
        if o.arguments is not None:
            for arg in o.arguments:
                init = arg.initializer
                if init is not None:
                    init.accept(self)

            for arg in o.arguments:
                self.visit_var(arg.variable)
        o.body.accept(self)

    def visit_func_def(self, o: 'mypy.nodes.FuncDef') -> None:
        name = o.name
        arg_names = getattr(o.type, "arg_names", None)
        arg_types = getattr(o.type, "arg_types", None)
        ret_type = getattr(o.type, "ret_type", None)
        if arg_names is None or arg_types is None or ret_type is None:
            self.navigate_func_def(o)
            return
        arg_types_str = [t.__repr__() for t in arg_types]
        args_str = ""
        if len(arg_names) == len(arg_types):
            args_str = ",".join([
                f"Named({name_arg},{type_arg})"
                for name_arg, type_arg in
                zip(arg_names, arg_types_str)
            ])
        annotation = f"[{args_str}][{ret_type.__repr__()}]"
        line = o.line
        column = o.column
        end_line = o.line
        end_column = column + len(name)
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {"line": end_line, "column": end_column}
        }
        fullname = o.fullname
        attrs = [
            attr for attr in dir(o)
            if attr.startswith("is_") and getattr(o, attr)]
        node_name = o.__class__.__name__
        type_info: MypyType = {
            "location": position,
            "name": name,
            "fullname": fullname,
            "node_name": node_name,
            "annotation": annotation,
            "attrs": attrs

        }
        self.types_info.append(type_info)
        self.navigate_func_def(o)

    def visit_class_def(self, o: 'mypy.nodes.ClassDef') -> None:
        name = o.name
        attrs = [
            attr for attr in dir(o.info)
            if attr.startswith("is_") and getattr(o.info, attr)]
        fullname = o.fullname
        line = o.line
        column = o.column
        end_line = o.line
        end_column = column + len(name)
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {"line": end_line, "column": end_column}
        }
        node_name = o.__class__.__name__
        annotation = fullname
        type_info: MypyType = {
            "location": position,
            "name": name,
            "fullname": fullname,
            "node_name": node_name,
            "annotation": annotation,
            "attrs": attrs
        }
        self.types_info.append(type_info)
        for d in o.decorators:
            d.accept(self)
        for base in o.base_type_exprs:
            base.accept(self)
        if o.metaclass:
            o.metaclass.accept(self)
        for v in o.keywords.values():
            v.accept(self)
        o.defs.accept(self)
        if o.analyzed:
            o.analyzed.accept(self)

    def visit_var(self, o: 'mypy.nodes.Var') -> None:

        name = o.name
        annotation = o.type.__repr__()
        node_name = o.__class__.__name__
        if o.type is None or o.column == -1:
            return
        column = o.type.column
        line = o.type.line
        fullname = o.fullname
        end_line = line
        end_column = column + len(name)
        attrs = [
            attr for attr in dir(o)
            if attr.startswith("is_") and getattr(o, attr)]
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {"line": end_line, "column": end_column}
        }
        type_info: MypyType = {
            "location": position,
            "name": name,
            "fullname": fullname,
            "node_name": node_name,
            "annotation": annotation,
            "attrs": attrs
        }
        self.types_info.append(type_info)

    def visit_name_expr(self, o: 'mypy.nodes.NameExpr') -> None:
        name = o.name
        line = o.line
        column = o.column
        end_line = o.end_line if o.end_line is not None else line
        end_column = o.column + len(name)
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {"line": end_line, "column": end_column}
        }
        node_name = o.__class__.__name__

        annotation = "MISSING"
        if isinstance(o.node, mypy.nodes.TypeInfo):
            annotation = o.node.fullname
        else:
            node_type = getattr(o.node, "type", None)
            if node_type is not None:
                annotation = node_type.__repr__()
            else:
                try:
                    if hash(self.tree.names[o.name].node) == hash(o.node):
                        annotation = o.name
                except KeyError:
                    pass

        attrs = [
            attr
            for attr in dir(o)
            if attr.startswith("is_") and getattr(o, attr)]
        type_info: MypyType = {
            "location": position,
            "name": name,
            "fullname": getattr(o, "fullname", None),
            "node_name": node_name,
            "annotation": annotation,
            "attrs": attrs
        }
        self.types_info.append(type_info)

    def visit_call_expr(self, o: 'mypy.nodes.CallExpr') -> None:

        args: List[mypy.nodes.Expression] = []
        extra: List[Union[str, Tuple[str, List[Any]]]] = []
        for i, kind in enumerate(o.arg_kinds):
            if kind in [mypy.nodes.ARG_POS, mypy.nodes.ARG_STAR]:
                args.append(o.args[i])
                if kind == mypy.nodes.ARG_STAR:
                    extra.append('VarArg')
            elif kind == mypy.nodes.ARG_NAMED:
                extra.append(('KwArgs', [o.arg_names[i], o.args[i]]))
            elif kind == mypy.nodes.ARG_STAR2:
                extra.append(('DictVarArg', [o.args[i]]))
            else:
                raise RuntimeError(f"unknown kind {kind}")

        node_name = o.__class__.__name__
        annotation = ""
        annotation = ",".join(node.__class__.__name__ for node in o.args)

        name = getattr(o.callee, "name", node_name)
        fullname = getattr(o.callee, "fullname", None)
        annotation = f"{fullname}[{annotation}]"

        line = o.line
        column = o.column
        end_line = o.end_line if o.end_line is not None else line
        end_column = o.column + len(name)
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {"line": end_line, "column": end_column}
        }
        attrs = [
            attr for attr in dir(o.callee)
            if attr.startswith("is_") and getattr(o.callee, attr)
        ]
        type_info: MypyType = {
            "location": position,
            "name": name,
            "fullname": fullname,
            "node_name": node_name,
            "annotation": annotation,
            "attrs": attrs
        }
        self.types_info.append(type_info)

        for a in o.args:
            a.accept(self)
        o.callee.accept(self)
        if o.analyzed:
            o.analyzed.accept(self)

    def visit_list_expr(self, o: 'mypy.nodes.ListExpr') -> None:
        line = o.line
        column = o.column
        end_line = o.end_line if o.end_line is not None else line
        end_column = getattr(o, "end_column", None)
        if end_column is None:
            end_column = column
        position: TokenLoc = {
            "start": {"line": line, "column": column},
            "stop": {
                "line": end_line,
                "column": end_column
            }
        }
        node_name = o.__class__.__name__
        annotations = []
        for item in o.items:
            # if hasattr(item, "node"):
            #     if hasattr(item.node, "type"):
            #         annotations.append(item.node.type.__repr__())
            #     elif hasattr(item.node, "fullname"):
            #         annotations.append(item.node.fullname)
            # elif hasattr(item, "value"):
            annotations.append(item.__class__.__name__)
        annotation = ",".join(annotations)

        attrs = [
            d for d in dir(o)
            if d.startswith("is_") and getattr(o, d)
        ]

        type_info: MypyType = {
            "location": position,
            "node_name": node_name,
            "name": "List",
            "fullname": getattr(o, "fullname", None),
            "annotation": annotation,
            "attrs": attrs
        }
        self.types_info.append(type_info)
        for item in o.items:
            item.accept(self)
