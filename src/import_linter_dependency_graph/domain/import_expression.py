from importlinter.domain.imports import ValueObject
from enum import Enum

from import_linter_dependency_graph.domain.defining_module_expression import DefiningModuleExpression
from import_linter_dependency_graph.domain.using_module_expression import UsingModuleExpression


class ImportType(Enum):
    IMPORTING = '->'
    IMPORTED = '<-'

class ImportExpression(ValueObject):

    _import_type: ImportType
    _defining_module_expr: DefiningModuleExpression
    _using_module_expr: UsingModuleExpression

    def __init__(self, import_type: ImportType, defining_module_expr: DefiningModuleExpression, using_module_expr: UsingModuleExpression):
        self._import_type = import_type
        self._defining_module_expr = defining_module_expr
        self._using_module_expr = using_module_expr

    @property
    def import_type(self)-> ImportType:
        return self._import_type

    @property
    def defining_module_expr(self)-> DefiningModuleExpression:
        return self._defining_module_expr

    @property
    def using_module_expr(self)-> UsingModuleExpression:
        return self._using_module_expr

    def __str__(self):
        if self._import_type == ImportType.IMPORTING:
            return f"{self._defining_module_expr}{self._import_type}{self._using_module_expr}"
        else:
            return f"{self._using_module_expr}{self._import_type}{self._defining_module_expr}"
