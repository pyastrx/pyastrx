a = 2

def global_change():
    global a
    a = 3

def unnecessary_global_keyword(b=2):
    global a
    b = b + a


def simple_def(c=1):
    return c


def global_keyword_in_strane_pos(b=2):
    b = b*2
    for i in range(10):
        global a
        a = a + 1


class ClassEx:
    def __init__(self, b=2):
        self.b = b

    def ok(self):
        print(a)

    def catch_unnecessary(self):
        global a
        return str(self.b)

    def catch(self):
        global a
        a = a + 1
        return str(self.b)
