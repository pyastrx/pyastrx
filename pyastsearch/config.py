from colorama import Fore


__default_expr_info = {
    "name": "",
    "description": "",
    "severity": "reject",
    "why": "",
    "reject": False,
}
__severity2color = {
    "reject": Fore.RED,
    "warning": Fore.YELLOW,
    "info": Fore.BLUE,
    "debug": Fore.MAGENTA,
    "default": Fore.GREEN,
}
__color_highlight = "white on magenta"