from sys import version_info

IS_PYTHON_37 = version_info.minor < 8


__severity2color = {
    "error": "red",
    "default": "green",
    "warning": "yellow",
    "info": "blue",
}
__color_highlight = "white on magenta"

__available_yaml = {
    "after_context": 3,
    "before_context": 3,
    "linter": False,
    "parallel": True,
    "interactive_files": False,
    "normalize_by_gast": True,
    "pagination": True
}

__available_yaml_folder = {
    "folder": ".",
    "parallel": True,
    "recursive": True,
    "exclude": [".venv", "docs", ".git", ".tox", ".pyastrx"],
}

_prompt_dialog_style = {
    'dialog':             'bg:#FFE873',
    'dialog frame.label': 'bg:#306998 #000000',
    'dialog.body':        'bg:#4B8BBE',
    'dialog shadow':      'bg:#306998',
}