import pytest
from opencog.atomspace import types

import mevis as mv
import shared


def test_api():
    atomspace = shared.load_moses_atomspace()

    # Plot
    # - default
    data_variants = (
        atomspace,              # AtomSpace
        list(atomspace)[0:5],   # list of Atoms
        mv.convert(atomspace),  # graph
    )
    for data in data_variants:
        mv.plot(data)

    # - backend
    for backend in ('d3', 'vis', 'three'):
        mv.plot(atomspace, backend)
    with pytest.raises(TypeError):
        mv.plot(atomspace, 42)
    with pytest.raises(ValueError):
        mv.plot(atomspace, 'nonsense')

    # - layout parameters
    other = dict(
        layout_scale_x=0.5,
        layout_scale_y=0.5,
        layout_mirror_x=True,
        layout_mirror_y=True,
        layout_center_x=True,
        layout_center_y=True,
    )
    known_layouts = [
        'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp',
        'bipartite', 'circular', 'kamada_kawai', 'planar', 'random', 'shell', 'spring',
        'spectral', 'spiral']
    for lm in known_layouts:
        mv.plot(atomspace, 'vis', lm, **other)
    for cx in (True, False):
        for cy in (True, False):
            mv.plot(atomspace, 'd3', 'neato', layout_center_x=cx, layout_center_y=cy)
    with pytest.raises(TypeError):
        mv.plot(atomspace, 'vis', 42, **other)
    with pytest.raises(ValueError):
        mv.plot(atomspace, 'vis', 'nonsense', **other)

    # - filter parameters
    type_name = 'OrLink'
    type_names = ['NotLink', 'OrLink']
    atom = list(atomspace)[5]
    atoms = list(atomspace)[3:5]
    atom_type = types.AndLink
    mix = [type_name, atom]

    def func(atom):
        return atom.type_name.startswith('O')

    known_targets = [type_name, type_names, type_names, func, atom, atoms, atom_type, mix]
    known_contexts = ['atom', 'in', 'out', 'both', 'in-tree', 'out-tree',
                      ('in', 2), ('out', 2), ('both', 2)]
    known_modes = ['include', 'exclude']
    for ft in known_targets:
        for fc in known_contexts:
            for fm in known_modes:
                mv.plot(atomspace, filter_target=ft, filter_context=fc, filter_mode=fm)

    # - annotated
    for annotated in (True, False):
        mv.plot(atomspace, graph_annotated=annotated)

    # - directed
    for directed in (True, False):
        mv.plot(atomspace, graph_directed=directed)

    # - annotation parameters
    mv.plot(
        atomspace,
        backend='d3',
        layout_method='neato',
        layout_scale_x=0.8,
        layout_scale_y=0.8,
        layout_mirror_x=True,
        layout_mirror_y=False,
        layout_center_x=True,
        layout_center_y=True,
        filter_target='AddLink',
        filter_context='out',
        filter_mode='include',
        graph_annotated=True,
        graph_directed=False,
        node_label='a',
        node_color='green',
        node_opacity=0.7,
        node_size=20,
        node_shape='hexagon',
        node_border_color='blue',
        node_border_size=2,
        node_label_color='red',
        node_label_size=12,
        node_hover='b',
        node_click='c',
        node_image=None,
        node_properties=dict(x=0, y=0),
        edge_label='d',
        edge_color='violet',
        edge_opacity=0.8,
        edge_size=3,
        edge_label_color='magenta',
        edge_label_size=6,
        edge_hover='e',
        edge_click='f',
    )

    def to_node_shape(atom):
        return 'circle' if atom.is_link() else 'hexagon'

    def to_edge_color(atom1, atom2):
        return 'pink' if atom1.is_link() and atom2.is_link() else None

    mv.plot(
        atomspace,
        node_label=lambda atom: atom.type_name if atom.is_link() else atom.type_name + atom.name,
        node_color=lambda atom: 'blue' if atom.is_link() else 'green',
        node_shape=to_node_shape,
        node_size=lambda atom: 10 if atom.is_node() else 20,
        node_hover=None,
        node_properties='tv',
        edge_label=lambda atom1, atom2: '{}-{}'.format(atom1.type_name, atom2.type_name),
        edge_color=to_edge_color,
        edge_size=lambda atom1, atom2: None if atom1.is_link() and atom2.is_link() else 3,
    )
