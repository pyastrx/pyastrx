"""A state machine with context using the State Pattern.

The state machine is responsible for the flow of the PyASTrX command
line interface (CLI).

A image diagram of the state machine can be found in the
`state_machine.png` file.

"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple, Type, Union
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.filters import completion_is_selected, has_completions
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.styles import Style
from rich import print as rprint

from pyastrx import __info__
from pyastrx.ast.things2ast import txt2ASTtxt
from pyastrx.config import _prompt_dialog_style
from pyastrx.data_typing import Config
from pyastrx.folder_utils import get_location_and_create
from pyastrx.frontend.manager import Manager
from pyastrx.report.stdout import paging_lxml, rich_paging
from pyastrx.search import Repo
from pyastrx.xml.misc import el_lxml2str

#  prompt dialog auto suggest history
if not Path(".pyastrx").exists():
    Path(".pyastrx").mkdir()
_PromptSessionExpr: PromptSession[str] = PromptSession(
    history=FileHistory('.pyastrx/history_new_expr.txt'))
_PromptSessionRules: PromptSession[str] = PromptSession(
    history=FileHistory('.pyastrx/history_rules.txt'))


char2color = {
    "s": "red1",
    "c": "bright_red",
    "l": "purple",
    "h": "yellow2",
    "q": "bright_red",
    "n": "spring_green2",
    "a": "magenta1",
    "t": "turquoise2",
    "o": "magenta1",
    "r": "orange_red1",
    "f": "purple",
    "x": "bright_green",
}


class State(ABC):
    """A abstract base class to represent a state in the state machine.

    Note:
        We are using the forward reference to deal with the
        circular type Context and State.
    """
    def __init__(self) -> None:
        self.title = ""
        self._context: "Context"

    @property
    def context(self) -> "Context":
        return self._context

    @context.setter
    def context(self, context: "Context") -> None:
        self._context = context

    @abstractmethod
    def run(self) -> None:
        pass

    def __del__(self) -> None:
        pass


PromptOpt = List[Tuple[str, str, Union[Type[State], str]]]


class StateInterface(State):
    """A abstract base class to represent a state interface
    in the state machine.

    Note:
        We are using the forward reference to deal with the
        circular type Context and State.
    """
    def __init__(self, title: str = "", help_text: str = "") -> None:
        self.title = title
        self.help_text = help_text
        self.pheader()

    @staticmethod
    def poptions(items: List[Tuple[str, str]]) -> None:
        for description, char in items:
            if char == "-":
                print(f"{char*50}")
                continue
            color = "white"
            if char in char2color:
                color = char2color[char]
            rprint(f"{' '*3}[bold {color}]{char}-{description}[/]")

    def default_prompt(
            self,
            options: PromptOpt) -> None:
        txt_opt, chars, states = zip(*options)
        command2state = {}
        valid_commands = []
        for _, char, state in zip(txt_opt, chars, states):
            if char == "-":
                continue
            command2state[char] = state
            valid_commands.append(char)
        command = None
        while command not in valid_commands:
            self.poptions(list(zip(txt_opt, chars)))
            command = prompt(":")
            command = command.lower()
        self.context.set_state(command2state[command])

    def pheader(self) -> None:
        """Print a header representing the current state in the stdout"""
        s = len(self.title)
        if s == 0:
            return
        rprint(f"\n{'='*s}\n{self.title}\n{'-'*s}")
        if self.help_text:
            rprint(self.help_text)
        print("-"*20)


class Context(Manager):
    def __init__(
            self, initial_state: Type[State],
            config: Config, repo: Repo) -> None:
        # super init manager
        super().__init__(config, repo)
        self._search_interface: Type[StateInterface] = InterfaceMain
        self.set_state(initial_state)

    @property
    def search_interface(self) -> Type[StateInterface]:
        return self._search_interface

    @search_interface.setter
    def search_interface(self, state: Type[StateInterface]) -> None:
        self._search_interface = state

    def set_state(
            self,
            state: Union[Type[State], Type[StateInterface]],
            **kwargs: str) -> None:
        state.context = self  # type: ignore
        self._state = state(**kwargs)


class StartState(State):
    def run(self) -> None:
        __info__()
        self.context.set_state(LoadFiles)


class LoadFiles(State):
    def run(self) -> None:
        self.context.load_files()
        self.context.set_state(
            InterfaceMain)


class Exit(State):
    def __init__(self, exit_code: int = 0) -> None:
        super().__init__()
        self.exit_code = exit_code

    def run(self) -> None:
        exit(self.exit_code)
        # if not self.context.interactive:
        #     exit()
        # while True:
        #     rprint("Are you sure [bold red]you want to exit?[/](y/n)")
        #     command = prompt(':')
        #     if command.lower() == "y":
        #         exit()
        #     elif command.lower() == "n":
        #         self.context.set_state(InterfaceMain())
        #         break


class InterfaceMain(StateInterface):
    def __init__(
            self, title: str = "Main interface",
            help_text: str = "") -> None:
        super().__init__(title=title, help_text=help_text)

    def run(self) -> None:
        self.context.resset_custom_expression()
        self.context.search_interface = InterfaceMain
        options: PromptOpt = [
            ("search using All rules", "a", SearchState),
            ("search using a Specific rule", "s", InterfaceRules),
            ("search using a selection of rules", "l", InterfaceSelectRules),
            ("search using a New expression", "n", InterfaceNewRule),
        ]
        if self.context.is_unique_file():
            options += [
                ("-", "-", ""),
                ("show XML", "x", ShowXML),
                ("show AST", "t", ShowAST),
                ("Open code", "o", ShowCode),
            ]
        else:
            options += [
                ("-", "-", ""),
                ("show Files", "f", InterfaceFiles),
            ]
        options += [
            ("-", "-", ""),
            ("Export AST and aXML", "e", InterfaceExport),
            ("-", "-", ""),
            ("Reload files", "r", LoadFiles),
            ("Reload YAML", "y", ReloadYAML),
            ("Help", "h", InterfaceHelp),
            ("Quit", "q", Exit)
        ]
        self.default_prompt(options)


class ReloadYAML(State):
    def run(self) -> None:
        self.context.reload_yaml()
        self.context.set_state(
            InterfaceMain)


class InterfaceExport(StateInterface):
    def __init__(self) -> None:
        self.title = "Export current files"
        super().__init__(title=self.title)

    def run(self) -> None:
        options: PromptOpt = [
            ("Export all aXML", "x", ExportXML),
            ("Export all AST", "t", ExportAST),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class InterfaceSelectRules(StateInterface):
    def get_options(self) -> Tuple[
            List[Tuple[int, str]],
            Dict[int, str],
            List[int]]:
        rules = self.context.config.rules
        options = []
        opt2xpath = {}
        default_values = []
        for i, (expression, info) in enumerate(rules.items()):
            name = info.name
            description = info.description
            why = info.why
            severity = info.severity
            str_info = f"({severity})-{name}-({why}):\n\t{description}"
            options.append((i, str_info))
            opt2xpath[i] = expression
            check = expression in self.context.selected_rules
            if check:
                default_values.append(i)
        return options, opt2xpath, default_values

    def run(self) -> None:
        options, opt2xpath, default_values = self.get_options()
        style = Style.from_dict(_prompt_dialog_style)
        if len(options) == 0:
            self.context.set_state(InterfaceMain)
            rprint(
                "\n[bold yellow]These rules will not match any pattern "
                + " in the provide files[/]\n")
            return

        dialog = checkboxlist_dialog(
            title="Rules selection",
            text="Choose which rules to use for the search",
            values=options,
            default_values=default_values,
            style=style
        )
        selected = dialog.run()
        selected = [] if selected is None else selected
        if len(selected) == 0:
            self.context.selected_rules = []
            self.context.set_state(InterfaceMain)
            return
        self.context.set_xpath_selection([opt2xpath[i] for i in selected])

        state = SearchState
        self.context.search_interface = InterfaceSelectRules

        self.context.set_state(state)


class InterfaceRules(StateInterface):
    def __init__(self) -> None:
        title = "Select a rule"
        help_text = "Type anything related to the rule"\
            + "or [bold red]q[/] to cancel"
        super().__init__(title=title, help_text=help_text)

    def get_humanized_rules(self) -> Tuple[List[str], Dict[str, str]]:
        self.context.search_interface = InterfaceRules

        rules = self.context.config.rules
        rules_str = []
        str2expression = {}
        for expression, info in rules.items():
            str_info = f"{info.name}({info.why}-){info.description}"
            rules_str.append(str_info)
            str2expression[str_info] = expression
        return rules_str, str2expression

    def run(self) -> None:
        key_bindings = KeyBindings()
        filter = has_completions & ~completion_is_selected

        @key_bindings.add("enter", filter=filter)
        def _(event: KeyPressEvent) -> None:
            event.current_buffer.go_to_completion(0)
            event.current_buffer.validate_and_handle()

        rules_str, str2expression = self.get_humanized_rules()
        rules_str = ["q"] + rules_str
        completer = FuzzyWordCompleter(rules_str)
        while True:
            command = _PromptSessionRules.prompt(
                ":",
                completer=completer,
                auto_suggest=AutoSuggestFromHistory(),
                complete_while_typing=True,
                key_bindings=key_bindings,
            )
            state: Type[State] = InterfaceMain
            if command == "q":
                break
            if command in str2expression:
                success = self.context.set_rule(str2expression[command])
                if success:
                    state = SearchState
                    break
        self.context.set_state(state)


class InterfaceNewRule(StateInterface):
    def __init__(self) -> None:
        title = "Search using a New expression"
        help_text = "Type a xpath expression"\
            + " and press enter to search"\
            + " or type [bold red]q[/] to cancel\n"
        super().__init__(title=title, help_text=help_text)

    def run(self) -> None:
        self.context.search_interface = InterfaceNewRule
        while True:
            command = _PromptSessionExpr.prompt(
                ":",
                auto_suggest=AutoSuggestFromHistory()
            )
            state: Type[State] = InterfaceMain
            if command == "q":
                break
            self.context.set_rule(command)
            state = SearchState
            break
        self.context.set_state(state)


class AvailableRules(State):
    def run(self) -> None:
        rules = self.context.config.rules
        for rule_info in rules.values():
            # list all attributes of the rule object
            for attr in dir(rule_info):
                if attr.startswith("_"):
                    continue
                rprint(f"{' '*3}{attr}: {getattr(rule_info, attr)}")
            rprint("\n")
        self.context.set_state(InterfaceMain)


class InterfaceHelp(StateInterface):
    def __init__(self) -> None:
        title = "Help"
        super().__init__(title=title)

    def run(self) -> None:
        options: PromptOpt = [
            ("available Rules", "r", AvailableRules),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class InterfaceFiles(StateInterface):
    def __init__(self) -> None:
        title = "Available Files"
        help_text = "Select a file to open"\
            + " or [bold red]q[/] to cancel"
        super().__init__(title=title, help_text=help_text)

    def run(self) -> None:
        key_bindings = KeyBindings()
        filter = has_completions & ~completion_is_selected

        @key_bindings.add("enter", filter=filter)
        def _(event: KeyPressEvent) -> None:
            event.current_buffer.go_to_completion(0)
            event.current_buffer.validate_and_handle()
        commands = ["q"] + self.context.repo.get_files()

        completer = FuzzyWordCompleter(commands)
        command = prompt(
            ":",
            completer=completer,
            complete_while_typing=True,
            key_bindings=key_bindings,
        )
        if command == "q":
            self.context.set_state(InterfaceMain)
        file = command
        try:
            self.context.set_current_file(file)
            help_text = f"{file}"
            self.context.set_state(InterfaceFile, file=help_text)
        except KeyError:
            self.context.set_state(InterfaceMain)


class InterfaceFile(StateInterface):
    def __init__(
            self, title: str = "File Options", file: str = "") -> None:
        super().__init__(
            title=title,
            help_text=f"[bold red]File[/]: {file}"
        )

    def run(self) -> None:

        options: PromptOpt = [
            ("show XML", "x", ShowXML),
            ("show AST", "t", ShowAST),
            ("Open file", "o", ShowCode),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class ShowCode(State):
    def run(self) -> None:
        code = self.context.current_fileinfo.txt
        rich_paging(code)
        self.context.set_state(FileCond)


class ShowXML(State):
    def run(self) -> None:
        axml = self.context.current_fileinfo.axml
        paging_lxml(axml)
        self.context.set_state(FileCond)


class ShowAST(State):
    def run(self) -> None:
        ast_txt = txt2ASTtxt(
            self.context.current_fileinfo.txt,
            normalize_ast=self.context.config.normalize_ast)
        rich_paging(ast_txt)
        self.context.set_state(FileCond)


class FileCond(State):
    def run(self) -> None:
        state: Type[State] = InterfaceFiles
        if self.context.is_unique_file():
            state = InterfaceMain
        self.context.set_state(state)


class ExportXML(State):
    def run(self) -> None:
        files = self.context.repo.get_files()
        for filename in files:
            file_info = self.context.repo.cache.get(filename)
            axml = file_info.axml
            axml_str = el_lxml2str(axml)
            export_location = get_location_and_create(
                ".pyastrx/export_data/axml/", filename, ".xml")

            with open(export_location, "w") as f:
                f.write(axml_str)
        self.context.set_state(InterfaceMain)


class ExportAST(State):
    def run(self) -> None:
        files = self.context.repo.get_files()
        for filename in files:
            file_info = self.context.repo.cache.get(filename)
            txt = file_info.txt
            ast_txt = txt2ASTtxt(
                txt,
                normalize_ast=self.context.config.normalize_ast
            )
            export_location = get_location_and_create(
                ".pyastrx/export_data/ast/", filename)

            with open(export_location, "w") as f:
                f.write(ast_txt)
        self.context.set_state(InterfaceMain)


class SearchState(State):
    def run(self) -> None:

        _, str_by_file, filter_rules = self.context.search()
        num_files = len(str_by_file)

        if not self.context._search_interface == InterfaceNewRule:
            self.context.filter_rules(filter_rules)
        interactive_files = self.context.config.interactive_files and num_files > 1 # noqa
        if not interactive_files:
            self.context.set_state(self.context._search_interface)
            return
        style = Style.from_dict(_prompt_dialog_style)
        selected_files: List[int] = []
        while True:
            options = [
                (i, filename)
                for i, (filename, _) in str_by_file.items()
            ]
            dialog = checkboxlist_dialog(
                title=f"Files selection: ({num_files} files matched the rules)",  # noqa
                text="To disable this dialog, set interactive_files to False in pyastrx.yaml",  # noqa
                values=options,
                default_values=selected_files,
                style=style
            )
            selected = dialog.run()
            selected = [] if selected is None else selected
            if len(selected) == 0:
                break
            selected_files = selected
            output_str = "".join(
                str_by_file[i][1] for i in selected
            )
            if self.context.config.pagination:
                rich_paging(output_str)
            else:
                rprint(output_str)
        self.context.set_state(self.context.search_interface)
