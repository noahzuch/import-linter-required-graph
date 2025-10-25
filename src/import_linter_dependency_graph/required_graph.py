import re
from typing import List

from grimp import ImportGraph

from importlinter.application import output
from importlinter.domain import fields

from importlinter import Contract, ContractCheck

from import_linter_dependency_graph.domain.import_expression import ImportExpression, ImportType
from import_linter_dependency_graph.fields.import_expression_field import ImportExpressionField


class RequiredGraphContract(Contract):

    """

    This contract requires every import staying inside a given root package to conform to at least one required import expression.
    Import Expressions use named capture groups (named variables here) to be more expressive. They can define for example the following rules:

    Shared modules importable by child modules in shareds parent package:
    root.[**?parent_package].shared.** <- root.[parent_package].**

    Module can import all modules in same or sub-package:
    root.[**parent_package].* -> root.[parent_package].**

    Port importable by adapter of same name (database_port.py importable by database_adapter.py but not filesystem_adapter.py):
    root.[**parent_package].ports.[port_name]port <- root.[parent_package].adapters.[port_name]adapter

    Import Expression are of the following regular Language:

    IMPORT_EXPRESSION :=
        DEFINING_MODULE_EXPRESSION -> USING_MODULE_EXPRESSION     # Import expression where importer defines variables and imported uses them
        | USING_MODULE_EXPRESSION <- DEFINING_MODULE_EXPRESSION   # Import expression where imported defines variables and importer uses them

    DEFINING_MODULE_EXPRESSION :=                                # Defining module expression contains variable definitions
        DEFINING_PACKAGE_EXPRESSION
        | DEFINING_PACKAGE_EXPRESSION . DEFINING_MODULE_EXPRESSION

    DEFINING_PACKAGE_EXPRESSION :=
        **                           # Wildcard for at least one package. Eager, meaning it consumes as many packages as possible
        | **?                        # Wildcard for at least one package. lazy, meaning it consumes as few packages as possible
        | *                          # Wildcard for exactly one package
        | [**VARIABLE_NAME]          # Wildcard for at least one package (eager), captured in the given variable name
        | [**?VARIABLE_NAME]         # Wildcard for at least one package (lazy), captured in the given variable name
        | PACKAGE_NAME               # Package name (possibly with wildcard variables)

    USING_MODULE_EXPRESSION :=                                # Using module expression uses variable definitions
        USING_PACKAGE_EXPRESSION
        | USING_PACKAGE_EXPRESSION . USING_MODULE_EXPRESSION

    USING_PACKAGE_EXPRESSION :=
        **                           # Wildcard for at least one package. Eager, meaning it consumes as many packages as possible
        | **?                        # Wildcard for at least one package. lazy, meaning it consumes as few packages as possible
        | *                          # Wildcard for exactly one package
        | [VARIABLE_NAME]            # Uses the captured variable of the given name from the defining module expression.
        | PACKAGE_NAME               # Package name (possibly with wildcard variables)

    PACKAGE_NAME :=
        PACKAGE_NAME_PART            # Part of package name only containing literal letters
        | [PACKAGE_NAME_PART]        # Part of package name representing a variable. In a defining module expression represents an eager wildcard. In a using module expression represents the captured variable
        | PACKAGE_NAME PACKAGE_NAME  # A package name can have any combination of literal letters and variables

    PACKAGE_NAME_PART := regular expression: [^\.]+
    VARIABLE_NAME := regular expression: [a-z_-]+

    TODO:

    - use already captured variable inside a defining module expression
    - include forbidden imports next to required imports
    - improve runtime
    """


    type_name = "import_graph"

    required_imports: List[ImportExpression] = fields.ListField(subfield=ImportExpressionField())
    root_package: fields.Module = fields.ModuleField()

    def check(self, graph: ImportGraph, verbose: bool) -> ContractCheck:
        modules = graph.find_matching_modules(f"{self.root_package.name}.**")
        invalid_imports = []

        for imported in modules:
            for importer in [importer for importer in graph.find_modules_that_directly_import(imported) if importer.startswith(self.root_package.name)]:
                if not self._is_import_valid(importer, imported):
                    invalid_imports.append(f"{importer} -> {imported}")
        return ContractCheck(kept=len(invalid_imports) == 0, metadata= {"invalid_imports": invalid_imports})

    def _is_import_valid(self, importer: str, imported: str):
        for import_expression in self.required_imports:
            if import_expression.import_type == ImportType.IMPORTING:
                importer_match = import_expression.defining_module_expr.pattern.fullmatch(importer)
                if importer_match is not None:
                    variable_dict = importer_match.groupdict()

                    imported_match = import_expression.using_module_expr.compile(variable_dict).fullmatch(imported)
                    if imported_match is not None:
                        return True
            else:
                imported_match = import_expression.defining_module_expr.pattern.fullmatch(imported)
                if imported_match is not None:
                    variable_dict = imported_match.groupdict()

                    importer_match = import_expression.using_module_expr.compile(variable_dict).fullmatch(importer)
                    if importer_match is not None:
                        return True

        return False


    def render_broken_contract(self, check: ContractCheck) -> None:

        for invalid_import in check.metadata["invalid_imports"]:
            output.print_error(invalid_import)
            output.new_line()


