import re

import pytest

from import_linter_dependency_graph.fields.module_expression_field import UsingModuleExpressionField


def test_compile_successful():
    using_module_expression = UsingModuleExpressionField().parse('foo.[bar].[baz]')
    actual = using_module_expression.compile({"bar":"bar_value", "baz":"baz_value"})

    assert actual == re.compile(r"foo\.bar_value\.baz_value")


def test_compile_escapes_special_characters():
    using_module_expression = UsingModuleExpressionField().parse('foo.[bar]')
    actual = using_module_expression.compile({"bar":"(bar_value)"})

    assert actual == re.compile(r"foo\.\(bar_value\)")


def test_compile__fails__if_variable_is_missing():
    using_module_expression = UsingModuleExpressionField().parse('foo.[bar].[baz]')
    with pytest.raises(ValueError):
        using_module_expression.compile({"bar":"(bar_value)"})