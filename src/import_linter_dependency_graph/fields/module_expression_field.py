from typing import Union, List
import re

from importlinter.domain.fields import Field, FieldValue, ValidationError

from import_linter_dependency_graph.domain.defining_module_expression import DefiningModuleExpression
from import_linter_dependency_graph.domain.using_module_expression import UsingModuleExpression

# In contrast to the Python name definition, we:
#  - disallow the dot character, as we work with packages and a dot is the separator character.
#  - allow leading and trailing _ and - chars, as this regex is also used to validate parts of a package name expression. We now are less limiting than python, which would simply result in no matches for the given expression but would not result in crashes.
_VALID_NAME_REGEX = r"[A-Za-z0-9_-]*"
_VALID_NAME_PATTERN = re.compile(f"^{_VALID_NAME_REGEX}$")

_NORMALIZE_NAME_REPLACE_PATTERN = re.compile(r"[-_]+")

def _normalize_name(name: str):
    return re.sub(_NORMALIZE_NAME_REPLACE_PATTERN, "_", name).lower()


_VALID_NON_WILDCARD_PACKAGE_NAME_REGEX = r"^(?:[A-Za-z0-9_-]|\[[A-Za-z0-9_-]+?\])*$"
_VALID_NON_WILDCARD_PACKAGE_NAME_PATTERN = re.compile(_VALID_NON_WILDCARD_PACKAGE_NAME_REGEX)

_REPLACE_VARIABLE_PATTERN = re.compile(r"\[([A-Za-z0-9_-]+?)\]")


_ANY_PACKAGE_REGEX=r"[^\.]+"
_ANY_PACKAGE_CHAIN_GREEDY_REGEX=r"[^\.]+(?:\.[^\.]+)*"
_ANY_PACKAGE_CHAIN_LAZY_REGEX=r"[^\.]+(?:\.[^\.]+)*?"

class DefiningModuleExpressionField(Field[DefiningModuleExpression]):

    def parse(self, module_expr: Union[str, List[str]]) -> DefiningModuleExpression:
        if isinstance(module_expr, list):
            raise ValidationError('Import Expression only allows single values')

        def validate_and_normalize_variable(name: str):
            if re.match(_VALID_NAME_PATTERN,name) is None:
                raise ValidationError(f"Name '{name}' is invalid. It should match the regular expression '{_VALID_NAME_REGEX}'")
            return _normalize_name(name)


        def parse_defining_non_wildcard_package(package_expr: str):
            if re.match(_VALID_NON_WILDCARD_PACKAGE_NAME_PATTERN, package_expr) is None:
                raise ValidationError(f"Package '{package_expr}' is invalid.")

            return re.sub(_REPLACE_VARIABLE_PATTERN, lambda match: rf"(?P<{_normalize_name(match.group(0)[1:-1])}>{_ANY_PACKAGE_REGEX})", package_expr)

        def parse_defining_package_expression(package_expr: str)-> str:
            if package_expr == '*':
                return _ANY_PACKAGE_REGEX
            elif package_expr == '**?':
                return _ANY_PACKAGE_CHAIN_LAZY_REGEX
            elif package_expr == '**':
                return _ANY_PACKAGE_CHAIN_GREEDY_REGEX
            elif package_expr.startswith('[**?'):
                return rf"(?P<{validate_and_normalize_variable(package_expr[4:-1])}>{_ANY_PACKAGE_CHAIN_LAZY_REGEX})"
            elif package_expr.startswith('[**'):
                return rf"(?P<{validate_and_normalize_variable(package_expr[3:-1])}>{_ANY_PACKAGE_CHAIN_GREEDY_REGEX})"
            else:
                return parse_defining_non_wildcard_package(package_expr)

        parsed_module_expr = r'\.'.join([parse_defining_package_expression(package_expr) for package_expr in module_expr.split('.')])

        return DefiningModuleExpression(regex_expression=parsed_module_expr)



class UsingModuleExpressionField(Field[UsingModuleExpression]):

    def parse(self, module_expr: Union[str, List[str]]) -> UsingModuleExpression:
        if isinstance(module_expr, list):
            raise ValidationError('Import Expression only allows single values')

        def parse_using_non_wildcard_package(package_expr: str):
            if re.match(_VALID_NON_WILDCARD_PACKAGE_NAME_PATTERN, package_expr) is None:
                raise ValidationError(f"Package '{package_expr}' is invalid.")

            return re.sub(_REPLACE_VARIABLE_PATTERN, lambda match: rf"(?={_normalize_name(match.group(0)[1:-1])})", package_expr)

        def parse_using_package_expression(package_expr: str)-> str:
            if package_expr == '*':
                return _ANY_PACKAGE_REGEX
            elif package_expr == '**?':
                return _ANY_PACKAGE_CHAIN_LAZY_REGEX
            elif package_expr == '**':
                return _ANY_PACKAGE_CHAIN_GREEDY_REGEX
            else:
                return parse_using_non_wildcard_package(package_expr)

        parsed_module_expr = r'\.'.join([parse_using_package_expression(package_expr) for package_expr in module_expr.split('.')])

        return UsingModuleExpression(regex_template=parsed_module_expr)