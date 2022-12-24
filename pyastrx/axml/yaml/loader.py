from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.parser import Parser
from yaml.constructor import Constructor
from yaml.resolver import Resolver

from pyastrx.axml.yaml.composer import Composer


class Loader(Reader, Scanner, Parser, Composer, Constructor, Resolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        Constructor.__init__(self)
        Resolver.__init__(self)
