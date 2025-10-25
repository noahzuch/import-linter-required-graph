import re

from importlinter.domain.imports import ValueObject


_REPLACE_VARIABLE_PATTERN = re.compile(r'\(\?=[A-Za-z0-9-_]+?\)')

class UsingModuleExpression(ValueObject):

    _regex_template: str

    def __init__(self, regex_template: str):
        self._regex_template = regex_template

    def compile(self, variables: dict[str,str]):

        def replace_variable(match: re.Match):
            variable_name = match.group(0)[3:-1]
            value = variables.get(variable_name, None)
            if value is None:
                raise ValueError(f"Requiring variable '{variable_name}'")

            return re.escape(value)

        return re.compile(_REPLACE_VARIABLE_PATTERN.sub(replace_variable, self._regex_template))

    def __str__(self):
        return self._regex_template