import os

import pytest

import mevis as mv
import shared


@pytest.mark.parametrize('filename', ('moses.scm',))  # TODO: more files
def test_load_and_store(tmpdir, filename):
    filepath = os.path.join(shared.IN_DIR, filename)

    # Load
    # - default
    atomspace1 = mv.load(filepath)
    n = atomspace1.size()
    with pytest.raises(FileNotFoundError):
        atomspace1 = mv.load('nonsense')
    # - verbose
    for verbose in (True, False):
        mv.load(filepath, verbose=verbose)
    # - method
    for method in ('basic', 'primitive', 'fast', 'python'):
        atsp = mv.load(filepath, method=method)
        assert atsp.size() == n
    with pytest.raises(ValueError):
        mv.load(filepath, method='nonsene')

    # Store
    with tmpdir.as_cwd():
        # - default
        mv.store(atomspace1, filename)

        # - verbose
        for verbose in (True, False):
            mv.store(atomspace1, filename+str(verbose), verbose=verbose)

        # - overwrite
        mv.store(atomspace1, filename, overwrite=True)
        with pytest.raises(FileExistsError):
            mv.store(atomspace1, filename, overwrite=False)

        # - method
        for method in ('basic', 'file-storage-node'):
            mv.store(atomspace1, filename+method, method=method)
        with pytest.raises(ValueError):
            mv.store(atomspace1, filepath+method, method='nonsene')

        # Re-import
        atomspace2 = mv.load(filename)
        n2 = atomspace2.size()
        atomspace3 = mv.load(filename+'file-storage-node')
        n3 = atomspace3.size()
    assert n2 == n
    assert n3 == n + 1  # FileStorageNode is added on export with 'file-storage-node'


def test_create():
    atomspace = mv.create()
    assert atomspace.size() == 0


def test_inspect():
    atomspace = shared.load_moses_atomspace()

    # AtomSpace
    result = mv.inspect(atomspace, count_details=False)
    assert isinstance(result, dict)
    assert len(result.keys()) == 3
    assert result['atoms'] == 13
    assert result['nodes'] == 4
    assert result['links'] == 9

    result = mv.inspect(atomspace, count_details=True)
    assert isinstance(result, dict)
    assert len(result.keys()) == 4
    assert result['atoms'] == 13
    assert result['nodes'] == 4
    assert result['links'] == 9
    assert result['types']['PredicateNode'] == 4
    assert result['types']['AndLink'] == 2
    assert result['types']['OrLink'] == 3
    assert result['types']['NotLink'] == 4

    # Graph
    graph = mv.convert(atomspace)
    result = mv.inspect(graph, count_details=False)
    assert isinstance(result, dict)
    assert len(result.keys()) == 2
    assert result['nodes'] == 13
    assert result['edges'] == 17

    graph = mv.convert(atomspace)
    result = mv.inspect(graph, count_details=True)
    assert isinstance(result, dict)
    assert len(result.keys()) == 4
    assert result['nodes'] == 13
    assert result['edges'] == 17
    assert result['node_properties']['label'] == 7
    assert result['node_properties']['color'] == 1
    assert result['node_properties']['shape'] == 1
    assert result['node_properties']['hover'] == 13
    assert result['edge_properties']['color'] == 1


def test_filter():
    atomspace = shared.load_moses_atomspace()

    # target and mode
    for mode in ['include', 'exclude']:
        for target in ['AndLink', 'OrLink', ['AndLink', 'NotLink']]:
            result = mv.filter(atomspace, target, mode=mode)
            assert len(result) > 0
            for atom in result:
                if mode == 'include':
                    assert atom.type_name in target
                else:
                    assert atom.type_name not in target

    # context
    known_contexts = [
        'in', 'out', 'both', 'in-tree', 'out-tree', ('in', 2), ('out', 2), ('both', 2)]
    for context in known_contexts:
        result = mv.filter(atomspace, target='AndLink', context=context)
        assert len(result) > 0
        for atom in result:
            assert isinstance(atom.type_name, str)
    for context in ['nonsense', ('a', 2), ('in', -1), ('in', 'b'), ('out', 'c'), ('both', 'd')]:
        with pytest.raises(ValueError):
            mv.filter(atomspace, target='AndLink', context=context)


def test_export(tmpdir):
    atomspace = shared.load_moses_atomspace()
    with tmpdir.as_cwd():
        graph = mv.convert(atomspace)
        mv.export(graph, 'test.gml')
        mv.export(graph, 'test.gml.gz')
        mv.export(graph, 'test.gml.bz2')
        with pytest.raises(ValueError):
            mv.export(graph, 'test.nons')
        with pytest.raises(FileExistsError):
            mv.export(graph, 'test.gml')
        mv.export(graph, 'test.gml', overwrite=True)


def test_try_scheme_eval():
    atomspace = shared.load_moses_atomspace()
    mv._internal.io._try_scheme_eval(atomspace, '(use-modules (opencog))')
    mv._internal.io._try_scheme_eval(atomspace, '(use-modules (opencog nonsense))')


def test_layout():
    atomspace_empty = mv.create()
    atomspace_moses = shared.load_moses_atomspace()

    known_layouts = [
        'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp',
        'bipartite', 'circular', 'kamada_kawai', 'planar', 'random', 'shell', 'spring',
        'spectral', 'spiral']
    for atomspace in [atomspace_empty, atomspace_moses]:
        for lm in known_layouts:
            mv.layout(atomspace, lm)
