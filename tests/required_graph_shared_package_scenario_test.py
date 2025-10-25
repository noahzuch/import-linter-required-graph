from grimp.adaptors.graph import ImportGraph

from import_linter_dependency_graph.import_graph import ImportGraphContract

"""
This scenario tests the shared package import rule. By this rule imports of a module M in package P are only allowed to:
    - modules contained in P or ones contained in any subpackage of P.
    - modules contained in a 'shared' package S where S is the direct subpackage of any intermediate package inside the path from the root package to P.
"""

def test_check_legal():
    import_graph = ImportGraph()
    import_graph.add_module('root')
    import_graph.add_module('root.shared')
    import_graph.add_module('root.shared.A')
    import_graph.add_module('root.foo')
    import_graph.add_module('root.foo.B')
    import_graph.add_module('root.foo.F')
    import_graph.add_module('root.foo.shared')
    import_graph.add_module('root.foo.shared.c')
    import_graph.add_module('root.foo.foobar')
    import_graph.add_module('root.foo.foobar.D')
    import_graph.add_module('root.bar')
    import_graph.add_module('root.bar.E')


    import_graph.add_import(importer='root.foo.B', imported='root.foo.foobar.D')
    import_graph.add_import(importer='root.foo.B', imported='root.shared.A')
    import_graph.add_import(importer='root.foo.B', imported='root.foo.F')
    import_graph.add_import(importer='root.foo.foobar.D', imported='root.foo.shared.C')
    import_graph.add_import(importer='root.foo.foobar.D', imported='root.shared.A')

    contract = ImportGraphContract('contract',{},{
        "root_package": 'root',
        "required_imports": [
            "[**parent].* -> [parent].**",
            "[**?shared_parent].shared.** <- [shared_parent].**"
        ]
    })

    result = contract.check(graph=import_graph, verbose=False)

    assert result.kept


def test_check_illegal():
    import_graph = ImportGraph()
    import_graph.add_module('root')
    import_graph.add_module('root.shared')
    import_graph.add_module('root.shared.A')
    import_graph.add_module('root.foo')
    import_graph.add_module('root.foo.B')
    import_graph.add_module('root.foo.F')
    import_graph.add_module('root.foo.shared')
    import_graph.add_module('root.foo.shared.c')
    import_graph.add_module('root.foo.foobar')
    import_graph.add_module('root.foo.foobar.D')
    import_graph.add_module('root.bar')
    import_graph.add_module('root.bar.E')


    import_graph.add_import(importer='root.foo.B', imported='root.bar.E')
    import_graph.add_import(importer='root.shared.A', imported='root.foo.shared.C')
    import_graph.add_import(importer='root.foo.B', imported='root.foo.F')
    import_graph.add_import(importer='root.foo.foobar.D', imported='root.foo.B')
    import_graph.add_import(importer='root.foo.foobar.D', imported='root.bar.E')

    contract = ImportGraphContract('contract',{},{
        "root_package": 'root',
        "required_imports": [
            "[**parent].* -> [parent].**",
            "[**?shared_parent].shared.** <- [shared_parent].**"
        ]
    })

    result = contract.check(graph=import_graph, verbose=False)

    assert result.kept == False
    assert set(result.metadata["invalid_imports"]) == {
        "root.foo.B -> root.bar.E",
        "root.shared.A -> root.foo.shared.C",
        "root.foo.foobar.D -> root.foo.B",
        "root.foo.foobar.D -> root.bar.E"
    }