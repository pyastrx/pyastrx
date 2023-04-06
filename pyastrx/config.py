__severity2color = {
    "error": "red",
    "default": "green",
    "warning": "yellow",
    "info": "blue",
}
__color_highlight = "white on magenta"

_prompt_dialog_style = {
    'dialog':             'bg:#FFE873',
    'dialog frame.label': 'bg:#306998 #000000',
    'dialog.body':        'bg:#4B8BBE',
    'dialog shadow':      'bg:#306998',
}
__default_conf = {
    "after_context": 3,
    "before_context": 3,
    "quiet": False,
    "interactive_files": False,
    "vscode_output": False,
    "pagination": True
}

__default_python_specs = {
    "python": {
        "folder": ".",
        "language": "python",
        "recursive": True,
        "exclude": [".venv", "docs", ".git", ".tox", ".pyastrx"],
        "rules": {
            "mutable-defaults": {
                "xpath": "//defaults/*[self::Dict or self::List or self::Set or self::Call]",  # noqa
                "description": "Can create bugs that are hard to find",
                "severity": "error",
                "why": "bad practice",
                "use_in_linter": True,
            }
        }
    }
}

__default_spec_confs = {
    "folder": ".",
    "recursive": True,
    "parallel": False,
    "exclude": [".venv", "docs", ".git", ".tox", ".pyastrx"],
}
