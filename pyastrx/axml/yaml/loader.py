from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.constructor import *
from yaml.resolver import *

from pyastrx.axml.yaml.composer import *


class Loader(Reader, Scanner, Parser, Composer, Constructor, Resolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self)
        Resolver.__init__(self)
