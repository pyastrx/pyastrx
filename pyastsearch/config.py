from colorama import Fore

__severity2color = {
    "reject": "red",
    "default": "green",
}
__color_highlight = "white on magenta"

__available_yaml = {
    "verbose": False,
    "print_xml": False,
    "abspaths": False,
    "after_context": 0,
    "before_context": 0,
    "print_matches": True,
}

__available_yaml_folder = {
    "folder": ".",
    "parallel": True,
    "recursive": True,
    "exclude": [".venv"],
}