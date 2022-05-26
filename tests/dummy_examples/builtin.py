def foo(dict, list):
    for key in dict:
        list.append(key)
    print(list)

data = {'a': 1, 'b': 2}
foo(data, [])
