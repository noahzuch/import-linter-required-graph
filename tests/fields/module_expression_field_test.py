import pytest

from importlinter.domain.fields import  ValidationError
from import_linter_dependency_graph.domain.defining_module_expression import DefiningModuleExpression
from import_linter_dependency_graph.domain.using_module_expression import UsingModuleExpression
from import_linter_dependency_graph.fields.module_expression_field import DefiningModuleExpressionField, \
    UsingModuleExpressionField


class TestDefiningModuleExpressionField:

    def test_simple_module(self):
        actual = DefiningModuleExpressionField().parse('foo.bar.baz')
        assert actual == DefiningModuleExpression(r'foo\.bar\.baz')

    def test_module_with_package_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.*.baz')
        assert actual == DefiningModuleExpression(r'foo\.[^\.]+\.baz')

    def test_module_with_eager_package_chain_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.**.baz')
        assert actual == DefiningModuleExpression(r'foo\.[^\.]+(?:\.[^\.]+)*\.baz')

    def test_module_with_lazy_package_chain_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.**?.baz')
        assert actual == DefiningModuleExpression(r'foo\.[^\.]+(?:\.[^\.]+)*?\.baz')

    def test_module_with_named_package_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.[my-var].baz')
        assert actual == DefiningModuleExpression(r'foo\.(?P<my_var>[^\.]+)\.baz')

    def test__validation_error__if_module_with_named_package_wildcard__has_invalid_character(self):
        with pytest.raises(ValidationError):
            DefiningModuleExpressionField().parse('foo.[my.var].baz')

    def test_module_with_eager_named_package_chain_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.[**my-var].baz')
        assert actual == DefiningModuleExpression(r'foo\.(?P<my_var>[^\.]+(?:\.[^\.]+)*)\.baz')

    def test__validation_error__if_module_with_eager_named_package_chain_wildcard__has_invalid_character(self):
        with pytest.raises(ValidationError):
            DefiningModuleExpressionField().parse('foo.[**my.var].baz')

    def test_module_with_lazy_named_package_chain_wildcard(self):
        actual = DefiningModuleExpressionField().parse('foo.[**?my-var].baz')
        assert actual == DefiningModuleExpression(r'foo\.(?P<my_var>[^\.]+(?:\.[^\.]+)*?)\.baz')

    def test__validation_error__if_module_with_lazy_named_package_chain_wildcard__has_invalid_character(self):
        with pytest.raises(ValidationError):
            DefiningModuleExpressionField().parse('foo.[**?my.var].baz')

    def test_module_with_part_of_package_including_variable__prefix(self):
        actual = DefiningModuleExpressionField().parse('foo.baz.[name]_port')
        assert actual == DefiningModuleExpression(r'foo\.baz\.(?P<name>[^\.]+)_port')

    def test_module_with_part_of_package_including_variable__suffix(self):
        actual = DefiningModuleExpressionField().parse('foo.baz.port_[name]')
        assert actual == DefiningModuleExpression(r'foo\.baz\.port_(?P<name>[^\.]+)')

    def test_module_with_part_of_package_including_variable__complex(self):
        actual = DefiningModuleExpressionField().parse('foo.baz.[foo]_some_[bar]_other_[baz]')
        assert actual == DefiningModuleExpression(r'foo\.baz\.(?P<foo>[^\.]+)_some_(?P<bar>[^\.]+)_other_(?P<baz>[^\.]+)')


class TestUsingModuleExpressionField:

    def test_simple_module(self):
        actual = UsingModuleExpressionField().parse('foo.bar.baz')
        assert actual == UsingModuleExpression(r'foo\.bar\.baz')

    def test_module_with_package_wildcard(self):
        actual = UsingModuleExpressionField().parse('foo.*.baz')
        assert actual == UsingModuleExpression(r'foo\.[^\.]+\.baz')

    def test_module_with_eager_package_chain_wildcard(self):
        actual = UsingModuleExpressionField().parse('foo.**.baz')
        assert actual == UsingModuleExpression(r'foo\.[^\.]+(?:\.[^\.]+)*\.baz')

    def test_module_with_lazy_package_chain_wildcard(self):
        actual = UsingModuleExpressionField().parse('foo.**?.baz')
        assert actual == UsingModuleExpression(r'foo\.[^\.]+(?:\.[^\.]+)*?\.baz')

    def test_module_with_named_package_wildcard(self):
        actual = UsingModuleExpressionField().parse('foo.[my-var].baz')
        assert actual == UsingModuleExpression(r'foo\.(?=my_var)\.baz')

    def test__validation_error__if_module_with_named_package_wildcard__has_invalid_character(self):
        with pytest.raises(ValidationError):
            UsingModuleExpressionField().parse('foo.(?=my.var).baz')

    def test_module_with_part_of_package_including_variable__prefix(self):
        actual = UsingModuleExpressionField().parse('foo.baz.[name]_port')
        assert actual == UsingModuleExpression(r'foo\.baz\.(?=name)_port')

    def test_module_with_part_of_package_including_variable__suffix(self):
        actual = UsingModuleExpressionField().parse('foo.baz.port_[name]')
        assert actual == UsingModuleExpression(r'foo\.baz\.port_(?=name)')

    def test_module_with_part_of_package_including_variable__complex(self):
        actual = UsingModuleExpressionField().parse('foo.baz.[foo]_some_[bar]-other_[baz]')
        assert actual == UsingModuleExpression(r'foo\.baz\.(?=foo)_some_(?=bar)-other_(?=baz)')

