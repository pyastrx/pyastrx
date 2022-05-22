"""A state machine with context using the State Pattern.

The state machine is responsible for the flow of the PyASTrX command
line interface (CLI).

A image diagram of the state machine can be found in the
`state_machine.png` file.

"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

import yaml
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.filters import completion_is_selected, has_completions
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.styles import Style
from rich import print as rprint

from pyastrx import __info__
from pyastrx.ast.things2ast import txt2ASTtxt
from pyastrx.config import __available_yaml as available_yaml
from pyastrx.config import _prompt_dialog_style
from pyastrx.folder_utils import get_location_and_create
from pyastrx.report import humanize as report_humanize
from pyastrx.report.stdout import paging_lxml, rich_paging
from pyastrx.search import Repo
from pyastrx.xml.misc import el_lxml2str

#  prompt dialog auto suggest history
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
        self._expression = ""
        self.current_file = None
        self.selected_rules = {}
        self._state = None
        self.repo = Repo()
        self._search_interface = InterfaceMain
        self.set_state(initial_state)

    def reload_yaml(self):
        with open(Path(".pyastrx.yaml").resolve(), "r") as f:
            _config = yaml.safe_load(f)
        for k in ("rules", "interactive_files", "pagination"):
            if k not in _config.keys():
                _config[k] = available_yaml[k]
            else:
                self._config[k] = _config[k]
        self._config["rules"] = _config["rules"]

    @property
    def normalize_by_gast(self) -> bool:
        return self._config["normalize_by_gast"]

    @property
    def rules(self) -> List[dict]:
        return self._config["rules"]

    @property
    def interactive_files(self) -> bool:
        return self._config["interactive_files"]

    @property
    def interactive(self) -> bool:
        return self._config["interactive"]

    @property
    def linter_mode(self) -> bool:
        return self._config["linter"]

    @property
    def expression(self) -> str:
        return self._expression

    @expression.setter
    def expression(self, xpath: str) -> None:
        self._expression = xpath

    @property
    def search_interface(self) -> State:
        return self._search_interface

    @search_interface.setter
    def search_interface(self, state: StateInterface) -> None:
        self._search_interface = state

    def use_pager(self) -> bool:
        return self._config["pagination"]

    def is_unique_file(self) -> bool:
        return len(self.repo.get_files()) == 1

    def is_folder(self) -> bool:
        return len(self.repo.get_files()) > 1

    def resset_custom_expression(self) -> None:
        self._expression = ""

    def set_current_file(self, file: str) -> None:
        info = self.repo.cache.get(file)
        self.current_fileinfo = info

    def set_xpath_selection(self, xpath_keys: List) -> None:
        self.selected_rules = xpath_keys

    def set_rule(self, xpath: str) -> bool:
        self.expression = xpath
        try:
            info = self._config["rules"][xpath]
            self.__current_rule = {xpath: info}
            return True
        except KeyError:
            self.__current_rule = {xpath: {}}
            return False

    def all_rules(self) -> List:
        """Return all rules in the config file

        TODO: This should return a only the rules that
        has been found in the current files

        """
        rules = self._config.get("rules")
        return rules

    def get_current_rules(self) -> dict:
        if self._expression:
            return self.__current_rule

        rules = self.all_rules()
        if len(self.selected_rules) > 0:
            rules = {k: rules[k] for k in self.selected_rules}

        if self.linter_mode:
            return {
                k: v for k, v in rules.items()
                if v.get("use_in_linter", True)}
        return rules

    def filter_rules(self, rules: List[dict]) -> None:
        for expression, num_matches in rules.items():
            if num_matches == 0:
                self.selected_rules = []
                del self._config["rules"][expression]

    def get_files(self) -> List:
        return self._config["files"]

    def is_parallel(self) -> bool:
        return self._config["parallel"]

    def set_state(self, state: State) -> None:
        state.context = self
        self._state = state

    def load_files(self) -> None:
        parallel = self.is_parallel()
        files = self.get_files()
        if len(files) == 1:
            file = files[0]
            self.repo.load_file(file, normalize_by_gast=self.normalize_by_gast)
            self.set_current_file(file)
        elif len(files) > 0:
            self.repo.load_files(
                files,
                parallel=parallel, normalize_by_gast=self.normalize_by_gast)
        else:
            self.repo.load_folder(
                self._config["folder"],
                normalize_by_gast=self.normalize_by_gast,
                parallel=parallel,
                exclude=self._config["exclude"],
                recursive=self._config["recursive"]
            )


class StartState(State):
    def run(self) -> None:
        if self.context.interactive:
            __info__()
        self.context.set_state(LoadFiles())


class LoadFiles(State):
    def run(self) -> None:
        self.context.load_files()
        if not self.context.interactive:
            self.context.set_state(SearchState())
        else:
            self.context.set_state(InterfaceMain())


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
    def start(self):
        self.title = "Main Menu"
        self.selected_rules = {}

    def run(self) -> None:
        self.context.resset_custom_expression()
        self.context.search_interface = InterfaceMain
        options = [
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
        self.context.set_state(InterfaceMain())


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


class InterfaceSelectRules(StateInterface):
    def start(self):
        self.title = "Select a rule"
        self.help_text = "Type anything related to the rule"\
            + "or [bold red]q[/] to cancel"

    def get_options(self):
        rules = self.context.all_rules()
        options = []
        opt2xpath = {}
        default_values = []
        for i, (expression, info) in enumerate(rules.items()):
            name = info.get("name", expression)
            description = info.get("description", "")
            why = info.get("why", "")
            str_info = f"{name}({why}-){description}"
            options.append((i, str_info))
            opt2xpath[i] = expression
            check = expression in self.context.selected_rules
            if check:
                default_values.append(i)
        return options, opt2xpath, default_values

    def run(self) -> None:
        options, opt2xpath, default_values = self.get_options()
        style = Style.from_dict(_prompt_dialog_style)

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
            self.context.set_state(InterfaceMain())
            return
        self.context.set_xpath_selection([opt2xpath[i] for i in selected])

        state = SearchState
        self.context.search_interface = InterfaceSelectRules

        self.context.set_state(state())


class InterfaceRules(StateInterface):
    def start(self):
        self.title = "Select a rule"
        self.help_text = "Type anything related to the rule"\
            + "or [bold red]q[/] to cancel"

    def get_humanized_rules(self):
        self.context.search_interface = InterfaceRules

        rules = self.context.rules
        rules_str = []
        str2expression = {}
        for expression, info in rules.items():
            name = info.get("name", expression)
            description = info.get("description", "")
            why = info.get("why", "")
            str_info = f"{name}({why}-){description}"
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
        self.context.search_interface = InterfaceNewRule
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
        rules = self.context.rules
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
        commands = ["q"] + self.context.repo.get_files()

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
        code = self.context.current_fileinfo.txt
        rich_paging(code)
        self.context.set_state(FileCond())


class ShowXML(State):
    def run(self) -> None:
        axml = self.context.current_fileinfo.axml
        paging_lxml(axml)
        self.context.set_state(FileCond())


class ShowAST(State):
    def run(self) -> None:
        ast_txt = txt2ASTtxt(
            self.context.current_fileinfo.txt,
            normalize_by_gast=self.context.normalize_by_gast)
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
        files = self.context.repo.get_files()
        for filename in files:
            file_info = self.context.repo.cache.get(filename)
            axml = file_info.axml
            axml_str = el_lxml2str(axml)
            export_location = get_location_and_create(
                ".pyastrx/export_data/axml/", filename, ".xml")

            with open(export_location, "w") as f:
                f.write(axml_str)
        self.context.set_state(InterfaceMain())


class ExportAST(State):
    def run(self) -> None:
        files = self.context.repo.get_files()
        for filename in files:
            file_info = self.context.repo.cache.get(filename)
            txt = file_info.txt
            ast_txt = txt2ASTtxt(
                txt,
                normalize_by_gast=self.context.normalize_by_gast
            )
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
        num_files = 0
        filter_rules = {k: 0 for k in rules.keys()}
        if is_unique_file:
            file = self.context.repo.get_file()
            matching_rules_by_line = self.context.repo.search_file(
                    file, rules,
                    before_context=config["before_context"],
                    after_context=config["after_context"],
                )
            if isinstance(rules, dict):
                for (lines, rules) in matching_rules_by_line.values():
                    for expr, info in rules.items():
                        filter_rules[expr] += info["num_matches"]
            output_str, num_matches = report_humanize.matches_by_filename(
                matching_rules_by_line, file)
        else:
            parent_folder = Path(".").resolve()
            matchng_by_file = self.context.repo.search_files(
                    rules,
                    before_context=config["before_context"],
                    after_context=config["after_context"],
                    parallel=config["parallel"],
                )

            str_by_file = {}
            output_str = ""

            for i, (filename, matching_rules_by_line) in enumerate(
                    matchng_by_file.items()):
                for (lines, rules) in matching_rules_by_line.values():
                    for expr, info in rules.items():
                        filter_rules[expr] += info["num_matches"]
                output_str_file, num_matches_file = \
                    report_humanize.matches_by_filename(
                            matching_rules_by_line, filename)
                if num_matches_file > 0:
                    str_by_file[i] = (
                        str(Path(filename).relative_to(parent_folder)),
                        output_str_file
                    )
                    num_matches += num_matches_file
                    num_files += 1
                    output_str += output_str_file
        if not self.context.interactive:
            rprint(output_str)
            exit_code = 1 if num_matches > 0 else 0
            self.context.set_state(Exit(exit_code))
        else:
            if not self.context._search_interface == InterfaceNewRule:
                self.context.filter_rules(filter_rules)
            interactive_files = self.context.interactive_files and num_files > 1
            if not interactive_files:
                if self.context.use_pager():
                    rich_paging(output_str)
                else:
                    rprint(output_str)
                self.context.set_state(self.context._search_interface())
                return
            style = Style.from_dict(_prompt_dialog_style)
            selected_files = []
            while True:
                options = [
                    (i, filename)
                    for i, (filename, _) in str_by_file.items()
                ]
                dialog = checkboxlist_dialog(
                    title=f"Files selection: ({num_files} files matched the rules)",
                    text="To disable this dialog, set interactive_files to False in pyastrx.yaml",
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
                if self.context.use_pager():
                    rich_paging(output_str)
                else:
                    rprint(output_str)
            self.context.set_state(self.context.search_interface())


