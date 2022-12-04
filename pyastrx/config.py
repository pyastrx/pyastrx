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
__available_yaml = {
    "after_context": 3,
    "before_context": 3,
    "quiet": False,
    "parallel": True,
    "interactive_files": False,
    "vscode_output": False,
    "specifications":
    {
        "python": {
            "folder": ".",
            "language": "python",
            "recursive": True,
            "exclude": [".venv", "docs", ".git", ".tox", ".pyastrx"],
            "rules": {
                "mutable-defaults": {
                    "xpath": "//defaults/*[self::Dict or self::List or self::Set or self::Call]", # noqa
                    "description": "Can create bugs that are hard to find",
                    "severity": "error",
                    "why": "bad practice",
                    "use_in_linter": True,
                    "normalize_ast": True

                }
            }
        }       
    },
    "pagination": True
    
}

__available_yaml_folder = {
    "folder": ".",
    "recursive": True,
    "parallel": True,
    "exclude": [".venv", "docs", ".git", ".tox", ".pyastrx"],
}
