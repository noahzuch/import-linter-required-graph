import re

from importlinter.domain.imports import ValueObject

class DefiningModuleExpression(ValueObject):

    _pattern: re.Pattern[str]

    def __init__(self, regex_expression: str):
        self._pattern = re.compile(regex_expression)

    @property
    def pattern(self):
        return self._pattern


    def __str__(self):
        return str(self._pattern)