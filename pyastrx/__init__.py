"""
PyASTrX

Search and lint your python code using simple xpath
expressions. No need to create python scripts and extensions to flake8 or
pylint

"""
from rich import print as rprint

__pkg_name__ = "PyASTrX"
__version__ = '0.4.2'
__author__ = 'Bruno Messias'
__github_author__ = '@devmessias'
__twitter__ = '@devmessias'
__author_email__ = 'devmessias@gmail.com'
__license__ = 'MIT'


def __info__() -> None:
    # print pkg_name centered in a 80 chars width
    hs = 60
    c = "!"
    rprint(f"{'-'*hs}")
    rprint(f"{c}{' '*(hs//2-1-len(__pkg_name__))}{__pkg_name__}{' '*(hs//2-1)}{c}") # noqa
    rprint(f"{'-'*hs}")
    rprint(*(
        f"[bold yellow] Version:[/] {__version__}\n",
        f"[bold yellow]Author:[/] {__author__}\n",
        f"[bold yellow]Github/Twitter:[/] {__github_author__}\n",
        f"[bold yellow]Email:[/] {__author_email__}\n",
    ))
    rprint(f"{'-'*hs}")
