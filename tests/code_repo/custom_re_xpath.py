from typing import TypeVar


class ExampleVar(TypeVar):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


def exampleFunctionVar(name: str, value: str):
    a = 2+2
    Var = "Wrong!"
    Var2 = ExampleVar(name, value)
    return ExampleVar(name, value)


class Example2(TypeVar):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value


class Example3Var(TypeVar):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value