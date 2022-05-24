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

a = 2
try:
    c = 1/a
except ImportError:
    c = 0

sum_r = 0
for i in range(10):
    sum_r += i

sum_r = 0
for i in range(10):
   a = i

for c in "abc":
    print(c)

for val in [1, 2, 3]:
    print(val)