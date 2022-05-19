def errada(arg1=2, arg3="http://www.google.com"):
    print(arg1, arg3)

url = "http://www.google.com"

def correta(arg1=2, arg3=None):
    print(arg1, arg3)

errada()
correta(arg3=url)