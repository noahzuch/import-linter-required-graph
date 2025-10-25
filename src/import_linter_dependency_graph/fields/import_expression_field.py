from typing import Union, List

from importlinter.domain.fields import Field, FieldValue,ValidationError

from import_linter_dependency_graph.domain.defining_module_expression import DefiningModuleExpression
from import_linter_dependency_graph.domain.import_expression import ImportExpression

from import_linter_dependency_graph.domain.import_expression import ImportType
from import_linter_dependency_graph.fields.module_expression_field import DefiningModuleExpressionField, \
    UsingModuleExpressionField


class ImportExpressionField(Field[ImportExpression]):

   def parse(self, expression: Union[str, List[str]]) -> ImportExpression:
        if isinstance(expression, list):
           raise ValidationError('Import Expression only allows single values')

        if '->' in expression:

            importer, _, imported = expression.partition('->')

            return ImportExpression(
                import_type= ImportType.IMPORTING,
                defining_module_expr=DefiningModuleExpressionField().parse(importer.strip()),
                using_module_expr=UsingModuleExpressionField().parse(imported.strip())
            )


        elif '<-' in expression:
            imported, _, importer = expression.partition('<-')

            return ImportExpression(
                import_type= ImportType.IMPORTED,
                defining_module_expr=DefiningModuleExpressionField().parse(imported.strip()),
                using_module_expr=UsingModuleExpressionField().parse(importer.strip())
            )

        else:
            raise ValidationError('')