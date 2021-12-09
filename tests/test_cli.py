import os

import mevis as mv
import shared


def test_entrypoint():
    exit_status = os.system('mevis -h')
    assert exit_status == 0

    exit_status = os.system('mevis -nonsense')
    assert exit_status != 0


def test_convert_and_plot(tmpdir):
    atomspace = shared.load_moses_atomspace()
    source = 'some_atomspace.scm'
    with tmpdir.as_cwd():
        mv.store(atomspace, source)

        # Generate a plot and display it
        cmd = 'mevis -i {}'.format(source)
        exit_status = os.system(cmd)
        assert exit_status == 0

        # Generate a graph object or plot and export it to a file
        for extension in ('html', 'jpg', 'png', 'svg', 'gml', 'gml.gz', 'gml.bz2'):
            target = 'test.' + extension
            assert not os.path.isfile(target)

            cmd = 'mevis -b d3 -i {} -o {}'.format(source, target)
            exit_status = os.system(cmd)
            assert exit_status == 0
            assert os.path.isfile(target)

            # default: overwrite fails
            cmd = 'mevis -b d3 -i {} -o {}'.format(source, target)
            exit_status = os.system(cmd)
            assert exit_status != 0

            # --force: overwrite is enforced
            for force, verbose in [('-f', '-v'), ('--force', '--verbose')]:
                cmd = 'mevis -b d3 -i {} -o {} {} {}'.format(source, target, force, verbose)
                exit_status = os.system(cmd)
                assert exit_status == 0

        # Invalid source
        cmd = 'mevis -i {} -o {}'.format('nonsense', target)
        exit_status = os.system(cmd)
        assert exit_status != 0

        # Invalid target
        cmd = 'mevis -i {} -o {}'.format(source, 'nonsense')
        exit_status = os.system(cmd)
        assert exit_status != 0

        # Existing target
        cmd = 'mevis -i {} -o {}'.format(source, target)
        exit_status = os.system(cmd)
        assert exit_status != 0


def test_filter(tmpdir):
    known_targets = [
        'AndLink',
        '''"['NotLink', 'OrLink']"''']
    known_contexts = [
        'atom', 'in', 'out', 'both', 'in-tree', 'out-tree',
        '''"('in', 2)"''', '''"('out', 2)"''', '''"('both', 2)"''']
    known_modes = ['include', 'exclude']
    atomspace = shared.load_moses_atomspace()
    source = 'some_atomspace.scm'
    with tmpdir.as_cwd():
        # Valid target, context and mode
        mv.store(atomspace, source)
        for ft in known_targets:
            for fc in known_contexts:
                for fm in known_modes:
                    cmd = 'mevis -i {} -o test.html -f -ft {} -fc {} -fm {}'.format(
                        source, ft, fc, fm)
                    exit_status = os.system(cmd)
                    assert exit_status == 0

        # Invalid context
        for fc in ['nonsense', '''"('in', -1)"''', '''"('nonsense', 2)"''']:
            cmd = 'mevis -i {} -o test.html -f -ft atom -fc {}'.format(source, fc)
            exit_status = os.system(cmd)
            assert exit_status != 0


def test_layout(tmpdir):
    known_layouts = [
        'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp',
        'bipartite', 'circular', 'kamada_kawai', 'planar', 'random', 'shell', 'spring',
        'spectral', 'spiral']
    atomspace = shared.load_moses_atomspace()
    source = 'some_atomspace.scm'
    with tmpdir.as_cwd():
        mv.store(atomspace, source)
        for lm in known_layouts:
            cmd = 'mevis -i {} -o test.html -f -l {}'.format(source, lm)
            exit_status = os.system(cmd)
            assert exit_status == 0


def test_kwargs(tmpdir):
    atomspace = shared.load_moses_atomspace()
    source = 'some_atomspace.scm'
    with tmpdir.as_cwd():
        mv.store(atomspace, source)

        # Valid kwargs
        valid_kwargs = [
            'edge_curvature=0.4',
            'node_label_data_source="id" show_node=False',
        ]
        for kwarg_str in valid_kwargs:
            cmd = 'mevis -i {} -o test.html -f -b d3 -l dot --kwargs {}'.format(source, kwarg_str)
            exit_status = os.system(cmd)
            assert exit_status == 0

        # Invalid kwargs
        invalid_kwargs = [
            '',
            'edge_curvature 0.4',
            'node_label_data_source "id" show_node=False',
            'node_label_data_source="id" show_node False',
            'nonsense=0.4',
        ]
        for kwarg_str in invalid_kwargs:
            cmd = 'mevis -i {} -o test.html -f -b d3 -l dot --kwargs {}'.format(source, kwarg_str)
            exit_status = os.system(cmd)
            assert exit_status != 0
