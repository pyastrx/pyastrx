"""A state machine with context using the State Pattern.

The state machine is responsible for the flow of the PyASTrX command
line interface (CLI).

A image diagram of the state machine can be found in the
`state_machine.png` file.

"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.filters import completion_is_selected, has_completions
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich import print as rprint

from pyastrx import __info__
from pyastrx.ast.things2ast import txt2ASTtxt
from pyastrx.folder_utils import get_location_and_create
from pyastrx.report import humanize as report_humanize
from pyastrx.report.stdout import paging_lxml, rich_paging
from pyastrx.search import Repo
from pyastrx.xml.misc import el_lxml2str

if not Path(".pyastrx").exists():
    Path(".pyastrx").mkdir()
_PromptSessionExpr = PromptSession(
    history=FileHistory('.pyastrx/history_new_expr.txt'))
_PromptSessionRules = PromptSession(
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
    def __init__(self):
        self.title = ""
        self._context = None

    @property
    def context(self) -> "Context":
        return self._context

    @context.setter
    def context(self, context: "Context") -> None:
        self._context = context

    @abstractmethod
    def run(self) -> None:
        pass

    def __del__(self):
        pass


class StateInterface(State):
    """A abstract base class to represent a state interface
    in the state machine.

    Note:
        We are using the forward reference to deal with the
        circular type Context and State.
    """
    def __init__(self, title: str = "", help_text: str ="") -> None:
        self.title = title
        self.help_text = help_text
        self.start()
        self.pheader()

    @abstractmethod
    def start(self) -> None:
        """This method is called right after the object is created.

        self.title,  and self.help_text should be
        set in this method.

        """
        pass

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
            options: List[Tuple[str, str, Union[State, str]]]) -> None:
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
            self.poptions(zip(txt_opt, chars))
            command = prompt(":")
            command = command.lower()
        self.context.set_state(command2state[command]())

    def pheader(self) -> None:
        """Print a header representing the current state in the stdout"""
        s = len(self.title)
        if s == 0:
            return
        rprint(f"\n{'='*s}\n{self.title}\n{'-'*s}")
        if self.help_text:
            rprint(self.help_text)
        print("-"*20)


class Context:
    def __init__(self, initial_state: State, config: dict) -> None:
        self._config = config
        self._interactive = config["interactive"]
        self._linter_mode = config["linter"]
        self._expression = ""
        self._current_file = None
        self.__current_rule = {}
        self._state = None
        self.repo = Repo()
        self._search_interface = InterfaceMain
        self.set_state(initial_state)

    @property
    def expression(self) -> str:
        return self._expression

    @expression.setter
    def expression(self, xpath: str) -> None:
        self._expression = xpath

    def is_unique_file(self) -> bool:
        return len(self.repo._files) == 1

    def is_folder(self) -> bool:
        return len(self.repo._files) > 1

    def resset_custom_expression(self) -> None:
        self._expression = ""

    def set_current_file(self, file: str) -> None:
        file = self.repo._files[0]
        info = self.repo._cache.get(file)
        self._current_file = info

    def set_rule(self, xpath: str) -> bool:
        self.expression = xpath
        try:
            info = self._config["rules"][xpath]
            self.__current_rule = {xpath: info}
            return True
        except KeyError:
            self.__current_rule = {xpath: {}}
            return False

    def get_current_rules(self) -> dict:
        if self._expression:
            return self.__current_rule
        rules = self._config["rules"]
        if self._linter_mode:
            return {
                k: v for k, v in rules.items()
                if v.get("use_in_linter", True)}
        return rules

    def set_state(self, state: State) -> None:
        state.context = self
        self._state = state


class StartState(State):
    def run(self) -> None:
        if self.context._interactive:
            __info__()
        self.context.set_state(LoadFiles())


class LoadFiles(State):
    def run(self) -> None:

        files = self.context._config.get("files")
        if len(files) == 1:
            file = files[0]
            self.context.repo.load_file(file)
            self.context.set_current_file(file)
        elif len(files) > 0:
            self.context.repo.load_files(
                files, parallel=self.context._config["parallel"])
        else:
            self.context.repo.load_folder(
                self.context._config["folder"],
                parallel=self.context._config["parallel"])
        if not self.context._interactive:
            self.context.set_state(SearchState())
        else:
            self.context.set_state(InterfaceMain())


class Exit(State):
    def __init__(self, exit_code: int = 0) -> None:
        super().__init__()
        self.exit_code = exit_code

    def run(self) -> None:
        exit(self.exit_code)
        # if not self.context._interactive:
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
    def start(self):
        self.title = "Main Menu"

    def run(self) -> None:
        self.context.resset_custom_expression()
        self.context._search_interface = InterfaceMain
        options = [
            ("search using All rules", "a", SearchState),
            ("search using a Specific rule", "s", InterfaceRules),
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
            ("Export results", "e", InterfaceExport),
            ("Reload files", "r", LoadFiles),
            ("Help", "h", InterfaceHelp),
            ("Quit", "q", Exit)
        ]
        self.default_prompt(options)


class InterfaceExport(StateInterface):
    def start(self):
        self.title = "Export current files"

    def run(self) -> None:
        options = [
            ("Export all aXML", "x", ExportXML),
            ("Export all AST", "t", ExportAST),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class InterfaceRules(StateInterface):
    def start(self):
        self.title = "Select a rule"
        self.help_text = "Type anything related to the rule"\
            + "or [bold red]q[/] to cancel"

    def get_humanized_rules(self):
        self.context._search_interface = InterfaceRules

        rules = self.context._config.get("rules")
        rules_str = []
        str2expression = {}
        for expression, info in rules.items():
            str_info = f"{info['name']}({info['why']}-){info['description']}"
            rules_str.append(str_info)
            str2expression[str_info] = expression
        return rules_str, str2expression

    def run(self) -> None:
        key_bindings = KeyBindings()
        filter = has_completions & ~completion_is_selected

        @key_bindings.add("enter", filter=filter)
        def _(event):
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
            if command == "q":
                state = InterfaceMain
                break
            if command in str2expression:
                success = self.context.set_rule(str2expression[command])
                if success:
                    state = SearchState
                    break
        self.context.set_state(state())


class InterfaceNewRule(StateInterface):
    def start(self):
        self.title = "Search using a New expression"
        self.help_text = "Type a xpath expression"\
            + " and press enter to search"\
            + " or type [bold red]q[/] to cancel\n"

    def run(self) -> None:
        self.context._search_interface = InterfaceNewRule
        while True:
            command = _PromptSessionExpr.prompt(
                ":",
                auto_suggest=AutoSuggestFromHistory()
            )
            if command == "q":
                state = InterfaceMain
                break
            self.context.set_rule(command)
            state = SearchState
            break
        self.context.set_state(state())


class AvailableRules(State):
    def run(self) -> None:
        rules = self.context._config.get("rules")
        for rule in rules.values():
            for key, val in rule.items():
                rprint(f"{' '*3}{key}: {val}")
            rprint("\n")
        self.context.set_state(InterfaceMain())


class InterfaceHelp(StateInterface):
    def start(self):
        self.title = "Help"

    def run(self) -> None:
        options = [
            ("available Rules", "r", AvailableRules),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class InterfaceFiles(StateInterface):
    def start(self):
        self.title = "Available Files"
        self.help_text = "Select a file to open"\
            + "or [bold red]q[/] to cancel"

    def run(self) -> None:
        key_bindings = KeyBindings()
        filter = has_completions & ~completion_is_selected

        @key_bindings.add("enter", filter=filter)
        def _(event):
            event.current_buffer.go_to_completion(0)
            event.current_buffer.validate_and_handle()
        commands = ["q"] + self.context.repo._files

        completer = FuzzyWordCompleter(commands)
        command = prompt(
            ":",
            completer=completer,
            complete_while_typing=True,
            key_bindings=key_bindings,
        )
        if command == "q":
            self.context.set_state(InterfaceMain())
        file = command
        self.context.set_current_file(file)
        help_text = f"{file}"
        self.context.set_state(InterfaceFile(help_text=help_text))


class InterfaceFile(StateInterface):
    def start(self):
        self.title = "File Options"

    def run(self) -> None:
        options = [
            ("show XML", "x", ShowXML),
            ("show AST", "t", ShowAST),
            ("Open file", "o", ShowCode),
            ("Cancel", "q", InterfaceMain)
        ]
        self.default_prompt(options)


class ShowCode(State):
    def run(self) -> None:
        code = self.context._current_file.txt
        rich_paging(code)
        self.context.set_state(FileCond())


class ShowXML(State):
    def run(self) -> None:
        axml = self.context._current_file.axml
        paging_lxml(axml)
        self.context.set_state(FileCond())


class ShowAST(State):
    def run(self) -> None:
        ast_txt = txt2ASTtxt(self.context._current_file.txt)
        rich_paging(ast_txt)
        self.context.set_state(FileCond())


class FileCond(State):
    def run(self) -> None:
        if self.context.is_unique_file():
            state = InterfaceMain
        else:
            state = InterfaceFiles
        self.context.set_state(state())


class ExportXML(State):
    def run(self) -> None:
        files = self.context.repo._files
        for filename in files:
            file_info = self.context.repo._cache.get(filename)
            axml = file_info.axml
            axml_str = el_lxml2str(axml)
            export_location = get_location_and_create(
                ".pyastrx/export_data/axml/", filename)

            with open(export_location, "w") as f:
                f.write(axml_str)
        self.context.set_state(InterfaceMain())


class ExportAST(State):
    def run(self) -> None:
        files = self.context.repo._files
        for filename in files:
            file_info = self.context.repo._cache.get(filename)
            txt = file_info.txt
            ast_txt = txt2ASTtxt(txt)
            export_location = get_location_and_create(
                ".pyastrx/export_data/ast/", filename)

            with open(export_location, "w") as f:
                f.write(ast_txt)
        self.context.set_state(InterfaceMain())


class SearchState(State):
    def run(self) -> None:
        config = self.context._config
        rules = self.context.get_current_rules()
        is_unique_file = self.context.is_unique_file()

        num_matches = 0
        if is_unique_file:
            file = self.context.repo._files[0]
            matching_rules_by_line = self.context.repo.search_file(
                    file, rules,
                    before_context=config["before_context"],
                    after_context=config["after_context"],
                )
            output_str, num_matches = report_humanize.matches_by_filename(
                matching_rules_by_line, file)
        else:
            matchng_by_file = self.context.repo.search_files(
                    rules,
                    before_context=config["before_context"],
                    after_context=config["after_context"],
                    parallel=config["parallel"],
                )

            output_str = ""
            for filename, matching_rules_by_file in matchng_by_file.items():
                output_str_file, num_matches_file = \
                        report_humanize.matches_by_filename(
                            matching_rules_by_file, filename)
                output_str += output_str_file
                num_matches += num_matches_file
        if not self.context._interactive:
            rprint(output_str)
            exit_code = 1 if num_matches > 0 else 0
            self.context.set_state(Exit(exit_code))
        else:
            rich_paging(output_str)
            self.context.set_state(self.context._search_interface())
