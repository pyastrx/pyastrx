"""All the xpath extensions should be defined here."""
import re
from typing import Dict, List, Any

from pyastrx.exceptions import MissingYAMLConfig


XPathContext = Any


class LXMLExtensions:
    def __init__(
            self, deny_dict: Dict[str, List[str]],
            allow_dict: Dict[str, List[str]]) -> None:
        self.deny_dict = deny_dict
        self.allow_dict = allow_dict

    def lxml_any_in(
            self, _: XPathContext,
            values_check: List[str], values: List[str]) -> bool:
        """Allows to check if the results of a xpath are inside
        of a list of another xpath results.

        Args:
            _: lxml.etree._XPathContext
            values_check: list of values to check
            values: list of values to check against
        Returns:
            bool: True if the values are inside of the values_check

        """

        for value in values:
            if value in values_check:
                return True
        return False

    def lxml_deny_list(
            self, _: XPathContext,
            list_name: str,
            values: List[str]) -> bool:
        """Allows to check if the results of a xpath is inside of
        a deny_list

        Args:
            _: lxml.etree._XPathContext
            values: list of values to check against
        Returns:
            bool: True if one of the values is inside of the deny_list

        """

        if self.deny_dict is None:
            raise MissingYAMLConfig(
                "march_params: deny_list",
                "Create first a deny_list inside of the yaml config")
        try:
            deny_list = self.deny_dict[list_name]
        except KeyError:
            raise MissingYAMLConfig(
                f"deny_list: {list_name}",
                f"Create first a attribute named {list_name} "
                + "inside of match_params:deny_list")
        for value in values:
            if value in deny_list:
                return True
        return False

    def lxml_allow_list(
            self, _: XPathContext,
            list_name: str,
            values: List[str]) -> bool:
        """Allows to check if the results of a xpath are inside
        of a list of another xpath results.

        Args:
            _: lxml.etree._XPathContext
            values: list of values to check against
        Returns:
            bool: True if the values can not be found in the allow_list

        """
        if self.allow_dict is None:
            raise MissingYAMLConfig(
                "march_params: allow_list",
                "Create first a allow_list inside of the yaml config")
        try:
            allow_list = self.allow_dict[list_name]
        except KeyError:
            raise MissingYAMLConfig(
                f"allow_list: {list_name}",
                f"Create first a attribute named {list_name} "
                + "inside of match_params:allow_list")

        for value in values:
            if value not in allow_list:
                return True
        return False

    def lxml_match(
            self, _: XPathContext,
            pattern: str, strings: List[str]) -> bool:
        for s in strings:
            if re.match(pattern, s) is not None:
                return True
        return False

    def lxml_search(
            self, _: XPathContext,
            pattern: str, strings: List[str]) -> bool:
        for s in strings:
            if re.search(pattern, s) is not None:
                return True
        return False


__all_lxml_ext__ = {
    "lxml_any_in": "any-in",
    "lxml_deny_list": "deny-list",
    "lxml_allow_list": "allow-list",
    "lxml_match": "match",
    "lxml_search": "search",
}

__lxml_namespaces__ = {"pyastrx": 'local-ns'}
