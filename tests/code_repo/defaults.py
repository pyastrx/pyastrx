from datetime import datetime


def print_func(a, b):
    print(a, b)


def should_catch(start_time, b=datetime.now()):

    try:
        print_func(start_time.timestamp(), b.timestamp())
    except Exception as e:
        return e
    return None


def correct(start_time, end_time):
    return start_time.timestamp() < end_time.timestamp()


def correct2(start_time, func=print_func):
    func(start_time.timestamp())


def should_catch2(a=[], b={}):
    try:
        print(a, b)
    except Exception as e:
        return e
    return None


class Example:
    def __init__(self, a=1):
        self.a = a

    def list_in_def(self, a=[2]):
        return a

    def set_in_def(self, a=set([1, 2, 3])):
        return a

    def dict_in_def(self, a={'a': 1}):
        return a