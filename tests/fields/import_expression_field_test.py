import re

import pytest

from importlinter.domain.fields import ValidationError
from import_linter_dependency_graph.domain.defining_module_expression import DefiningModuleExpression
from import_linter_dependency_graph.domain.import_expression import ImportType
from import_linter_dependency_graph.domain.using_module_expression import UsingModuleExpression
from import_linter_dependency_graph.fields.import_expression_field import ImportExpressionField


def test_importing_direction():
    actual = ImportExpressionField().parse('foo.bar -> foobar')
    assert actual.import_type == ImportType.IMPORTING
    assert actual.defining_module_expr == DefiningModuleExpression(r'foo\.bar')
    assert actual.using_module_expr == UsingModuleExpression(r'foobar')

def test_imported_direction():
    actual = ImportExpressionField().parse('foo.bar <- foobar')
    assert actual.import_type == ImportType.IMPORTED
    assert actual.defining_module_expr == DefiningModuleExpression(r'foo\.bar')
    assert actual.using_module_expr == UsingModuleExpression(r'foobar')


def test_validation_error__if_no_direction():
    with pytest.raises(ValidationError):
        ImportExpressionField().parse('foo.bar')

def test_validation_error__if_malformed_direction():
    with pytest.raises(ValidationError):
        ImportExpressionField().parse('foo.bar --> foobar')

def test_validation_error__if_multiple_direction():
    with pytest.raises(ValidationError):
        ImportExpressionField().parse('foo.bar -> foobar -> baz')