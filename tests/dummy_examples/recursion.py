def recursion_f(n):
    if n == 0:
        return 0
    else:
        return n + recursion_f(n-1)

def no_recursion(a, b):
    recursion = a+b
    return recursion

def sub_recursion_f(a, b):
    c = a+b
    if c == 0:
        return 0
    def af(a, b):
        return sub_recursion_f(a, b)
    return c + af(a, b)


def subsub_recursion(a, b):
    def recursion2_f(n):
        if n == 0:
            return 0
        else:
            return n + recursion2_f(n-1)
    return recursion2_f(a+b)

def _rec_class_fake(n):
    return n

class A:
    def __init__(self) -> None:
        pass
    def _rec_class(self, n):
        if n == 0:
            return 0
        else:
            return n + self._rec_class(n-1)

    def _rec_class_fake(self, n):
        if n == 0:
            return 0
        else:
            return n + _rec_class_fake(n-1)
    def in_class(self, n):
        def in_recursion_f(n):
            if n == 0:
                return 0
            else:
                return n + in_recursion_f(n-1)
        return in_recursion_f(n)