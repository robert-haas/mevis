from collections.abc import Callable as _Callable

import networkx as _nx
from opencog.type_constructors import AtomSpace as _AtomSpace

from .args import check_arg as _check_arg


def convert(data, graph_annotated=True, graph_directed=True,
            node_label=None, node_color=None, node_opacity=None, node_size=None, node_shape=None,
            node_border_color=None, node_border_size=None,
            node_label_color=None, node_label_size=None, node_hover=None, node_click=None,
            node_image=None, node_properties=None,
            edge_label=None, edge_color=None, edge_opacity=None, edge_size=None,
            edge_label_color=None, edge_label_size=None, edge_hover=None, edge_click=None):
    """Convert an Atomspace or list of Atoms to a NetworkX graph with annotations.

    Several arguments accept a Callable.

    - In case of node annotations, the Callable gets an Atom as input,
      which the node represents in the graph.
      The Callable needs to return one of the other types accepted by the argument,
      e.g. ``str`` or ``int``/``float``.
    - In case of edge annotations, the Callable gets two Atoms as input,
      which the edge connects in the graph.
      The Callable needs to return one of the other types accepted by the argument,
      e.g. ``str`` or ``int``/``float``.

    Several arguments accept a color, which can be in following formats:

    - Name: ``"black"``, ``"red"``, ``"green"``, ...
    - Color code

      - 6 digit hex RGB code: ``"#05ac05"``
      - 3 digit hex RGB code: ``"#0a0"`` (equivalent to ``"#00aa00"``)

    Parameters
    ----------
    data : Atomspace, list of Atoms
        Input that gets converted to a graph.
    graph_annotated : bool
        If ``False``, no annotations are added to the graph. This could be used for
        converting large AtomSpaces quickly to graphs that use less RAM and can
        be exported to smaller files (e.g. also compressed as gml.gz) for inspection
        with other tools.
    graph_directed : bool
        If ``True``, a NetworkX DiGraph is created. If ``False``, a NetworkX Graph is created.
    node_label : str, Callable
        Set a label for each node, which is shown as text below it.
    node_color : str, Callable
        Set a color for each node, which becomes the fill color of its shape.
    node_opacity : float between 0.0 and 1.0
        Set an opacity for each node, which becomes the opacity of its shape.

        Caution: This is only supported by d3.
    node_size : int, float, Callable
        Set a size for each node, which becomes the height and width of its shape.
    node_shape :  str, Callable
        Set a shape for each node, which is some geometrical form that has the
        node coordinates in its center.

        Possible values: ``"circle"``, ``"rectangle"``, ``"hexagon"``

    node_border_color : str, Callable
        Set a border color for each node, which influences the border drawn around its shape.
    node_border_size : int, float, Callable
        Set a border size for each node, which influences the border drawn around its shape.
    node_label_color : str, Callable
        Set a label color for each node, which determines the font color
        of the text below the node.
    node_label_size : int, float, Callable
        Set a label size for each node, which determines the font size
        of the text below the node.
    node_hover : str, Callable
        Set a hover text for each node, which shows up besides the mouse cursor
        when hovering over a node.
    node_click : str, Callable
        Set a click text for each node, which shows up in a div element below the plot
        when clicking on a node and can easily be copied and pasted.
    node_image : str, Callable
        Set an image for each node, which appears within its shape.

        Possible values:

        - URL pointing to an image
        - Data URL encoding the image
    node_properties : str, dict, Callable
        Set additional properties for each node, which may not immediately be translated
        into a visual element, but can be chosen in the data selection menu in the
        interactive HTML visualizations to map them on some plot element.
        These properties also appear when exporting a graph to a file in a format
        such as GML and may be recognized by external visualization tools.
        Note that a Callable needs to return a dict in this case, and each key becomes
        a property, which is equivalent to the other properties such as node_size and
        node_color.

        Special cases:

        - ``node_properties="tv"`` is a shortcut for using a function that returns
          ``{"mean": atom.tv.mean, "confidence": atom.tv.confidence}``
        - Keys ``"x"``, ``"y"`` and ``"z"`` properties are translated into node coordinates.

        Examples:

        - ``dict(x=0.0)``: This fixes the x coordinate of each node to 0.0, so that the
          JavaScript layout algorithm does not influence it, but the nodes remain
          free to move in the y and z directions.
        - ``lambda atom: dict(x=2.0) if atom.is_node() else None``:
          This fixes the x coordinate of each Atom of type Node to 2.0
          but allows each Atom of type Link to move freely.
        - ``lambda atom: dict(y=-len(atom.out)*100) if atom.is_link() else dict(y=0)``
          This fixes the y coordinates of Atoms at different heights. Atoms of type Node
          are put at the bottom and Atoms of type Link are ordered by the number of their
          outgoing edges. The results is a hierarchical visualization that has some
          similarity with the "dot" layout.
        - ``lambda atom: dict(x=-100) if atom.is_node() else dict(x=100)``:
          This fixes the x coordinate of Node Atoms at -100 and of Link Atoms at 100.
          The results is a visualization with two lines of nodes that has some
          similarity with the "bipartite" layout.
    edge_label : str, Callable
        Set a label for each edge, which becomes the text plotted in the middle of the edge.
    edge_color : str, Callable
        Set a color for each edge, which becomes the color of the line representing the edge.
    edge_opacity : int, float, Callable
        Set an opacity for each edge, which allows to make it transparent to some degree.
    edge_size : int, float, Callable
        Set a size for each edge, which becomes the width of the line representing the edge.
    edge_label_color : str, Callable
        Set a color for each edge label, which becomes the color of the text in the midpoint
        of the edge.
    edge_label_size : int, float, Callable
        Set a size for each edge label, which becomes the size of the text in the midpoint
        of the edge.
    edge_hover : str, Callable
    edge_click : str, Callable

    Returns
    -------
    graph : NetworkX Graph or DiGraph
        Whether an undirected or directed graph is created depends on the argument "directed".

    """
    # Argument processing
    _check_arg(data, 'data', (list, _AtomSpace))

    _check_arg(graph_annotated, 'graph_annotated', bool)
    _check_arg(graph_directed, 'graph_directed', bool)

    _check_arg(node_label, 'node_label', (str, _Callable), allow_none=True)
    _check_arg(node_color, 'node_color', (str, _Callable), allow_none=True)
    _check_arg(node_opacity, 'node_opacity', (int, float, _Callable), allow_none=True)
    _check_arg(node_size, 'node_size', (int, float, _Callable), allow_none=True)
    _check_arg(node_shape, 'node_shape', (str, _Callable), allow_none=True)
    _check_arg(node_border_color, 'node_border_color', (str, _Callable), allow_none=True)
    _check_arg(node_border_size, 'node_border_size', (int, float, _Callable), allow_none=True)
    _check_arg(node_label_color, 'node_label_color', (str, _Callable), allow_none=True)
    _check_arg(node_label_size, 'node_label_size', (int, float, _Callable), allow_none=True)
    _check_arg(node_hover, 'node_hover', (str, _Callable), allow_none=True)
    _check_arg(node_click, 'node_click', (str, _Callable), allow_none=True)
    _check_arg(node_image, 'node_image', (str, _Callable), allow_none=True)
    _check_arg(node_properties, 'node_properties', (str, dict, _Callable), allow_none=True)

    _check_arg(edge_label, 'edge_label', (str, _Callable), allow_none=True)
    _check_arg(edge_color, 'edge_color', (str, _Callable), allow_none=True)
    _check_arg(edge_opacity, 'edge_opacity', (int, float, _Callable), allow_none=True)
    _check_arg(edge_size, 'edge_size', (int, float, _Callable), allow_none=True)
    _check_arg(edge_label_color, 'edge_label_color', (str, _Callable), allow_none=True)
    _check_arg(edge_label_size, 'edge_label_size', (int, float, _Callable), allow_none=True)
    _check_arg(edge_hover, 'edge_hover', (str, _Callable), allow_none=True)
    _check_arg(edge_click, 'edge_click', (str, _Callable), allow_none=True)

    # Prepare annoation functions
    if graph_annotated:
        node_ann = prepare_node_func(
            node_label, node_color, node_opacity, node_size, node_shape, node_border_color,
            node_border_size, node_label_color, node_label_size, node_hover, node_click,
            node_image, node_properties)
        edge_ann = prepare_edge_func(
            edge_label, edge_color, edge_opacity, edge_size,
            edge_label_color, edge_label_size, edge_hover, edge_click)
    else:
        empty = dict()

        def node_ann(atom):
            return empty

        def edge_ann(atom1, atom2):
            return empty

    # Create the NetworkX graph
    graph = _nx.DiGraph() if graph_directed else _nx.Graph()
    # 0) Set graph annotations
    graph.graph['node_click'] = '$hover'  # node_click will by default show content of node_hover
    # 1) Add vertices and their annotations
    for atom in data:
        graph.add_node(to_uid(atom), **node_ann(atom))
    # 2) Add edges and their annotations (separate step to exclude edges to filtered vertices)
    for atom in data:
        uid = to_uid(atom)
        if atom.is_link():
            # for all that is incoming to the Atom
            for atom2 in atom.incoming:
                uid2 = to_uid(atom2)
                if uid2 in graph.nodes:
                    graph.add_edge(uid2, uid, **edge_ann(atom2, atom))
            # for all that is outgoing of the Atom
            for atom2 in atom.out:
                uid2 = to_uid(atom2)
                if uid2 in graph.nodes:
                    graph.add_edge(uid, uid2, **edge_ann(atom, atom2))
    return graph


def prepare_node_func(node_label, node_color, node_opacity, node_size, node_shape,
                      node_border_color, node_border_size, node_label_color, node_label_size,
                      node_hover, node_click, node_image, node_properties):
    """Prepare a function that calculates all annoations for a node representing an Atom."""
    # individual node annotation functions
    node_label = use_node_def_or_str(node_label, node_label_default)
    node_color = use_node_def_or_str(node_color, node_color_default)
    node_opacity = use_node_def_or_num(node_opacity, node_opacity_default)
    node_size = use_node_def_or_num(node_size, node_size_default)
    node_shape = use_node_def_or_str(node_shape, node_shape_default)
    node_border_color = use_node_def_or_str(node_border_color, node_border_color_default)
    node_border_size = use_node_def_or_num(node_border_size, node_border_size_default)
    node_label_color = use_node_def_or_str(node_label_color, node_label_color_default)
    node_label_size = use_node_def_or_num(node_label_size, node_label_size_default)
    node_hover = use_node_def_or_str(node_hover, node_hover_default)
    node_click = use_node_def_or_str(node_click, node_click_default)
    node_image = use_node_def_or_str(node_image, node_image_default)

    # special case: additional user-defined node properties by a function that returns a dict
    if node_properties is None:
        node_properties = node_properties_default
    elif isinstance(node_properties, dict):
        val = node_properties

        def node_properties(atom):
            return val
    elif node_properties == 'tv':
        node_properties = node_properties_tv

    # combined node annotation function: calls each of the individual ones
    name_func = (
        ('label', node_label),
        ('color', node_color),
        ('opacity', node_opacity),
        ('size', node_size),
        ('shape', node_shape),
        ('border_color', node_border_color),
        ('border_size', node_border_size),
        ('label_color', node_label_color),
        ('label_size', node_label_size),
        ('hover', node_hover),
        ('click', node_click),
        ('image', node_image),
    )

    def func(atom):
        data = {}
        for n, f in name_func:
            val = f(atom)
            if val is not None:
                data[n] = val
        try:
            data.update(node_properties(atom))
        except Exception:
            pass
        return data
    return func


def prepare_edge_func(edge_label, edge_color, edge_opacity, edge_size, edge_label_color,
                      edge_label_size, edge_hover, edge_click):
    """Prepare a function that calculates all annoations for an edge between Atoms."""
    # individual edge annotation functions
    edge_label = use_edge_def_or_str(edge_label, edge_label_default)
    edge_color = use_edge_def_or_str(edge_color, edge_color_default)
    edge_opacity = use_edge_def_or_num(edge_opacity, edge_opacity_default)
    edge_size = use_edge_def_or_num(edge_size, edge_size_default)
    edge_label_color = use_edge_def_or_str(edge_label_color, edge_label_color_default)
    edge_label_size = use_edge_def_or_num(edge_label_size, edge_label_size_default)
    edge_hover = use_edge_def_or_str(edge_hover, edge_hover_default)
    edge_click = use_edge_def_or_str(edge_click, edge_click_default)

    # combined edge annotation function: calls each of the individual ones
    name_func = (
        ('label', edge_label),
        ('color', edge_color),
        ('opacity', edge_opacity),
        ('size', edge_size),
        ('label_color', edge_label_color),
        ('label_size', edge_label_size),
        ('hover', edge_hover),
        ('click', edge_click),
    )

    def func(atom1, atom2):
        data = {}
        for n, f in name_func:
            val = f(atom1, atom2)
            if val is not None:
                data[n] = val
        return data
    return func


def use_node_def_or_str(given_value, default_func):
    """Transform a value of type (None, str, Callable) to a node annotation function."""
    # Default: use pre-defined function from this module
    if given_value is None:
        func = default_func
    # Transform: value to function that returns the value
    elif isinstance(given_value, str):
        given_value = str(given_value)

        def func(atom):
            return given_value
    # Passthrough: value itself is a function
    else:
        func = given_value
    return func


def use_node_def_or_num(given_value, default_func):
    """Transform a value of type (None, int, float, Callable) to a node annotation function."""
    # Default: use pre-defined function from this module
    if given_value is None:
        func = default_func
    # Transform: value to function that returns the value
    elif isinstance(given_value, (int, float)):
        given_value = float(given_value)

        def func(atom):
            return given_value
    # Passthrough: value itself is a function
    else:
        func = given_value
    return func


def use_edge_def_or_str(given_value, default_func):
    """Transform a value of type (None, str, Callable) to an edge annotation function."""
    # Default: use pre-defined function from this module
    if given_value is None:
        func = default_func
    # Transform: value to function that returns the value
    elif isinstance(given_value, str):
        given_value = str(given_value)

        def func(atom1, atom2):
            return given_value
    # Passthrough: value itself is a function
    else:
        func = given_value
    return func


def use_edge_def_or_num(given_value, default_func):
    """Transform a value of type (None, int, float, Callable) to an edge annotation function."""
    # Default: use pre-defined function from this module
    if given_value is None:
        func = default_func
    # Transform: value to function that returns the value
    elif isinstance(given_value, (int, float)):
        given_value = float(given_value)

        def func(atom1, atom2):
            return given_value
    # Passthrough: value itself is a function
    else:
        func = given_value
    return func


def to_uid(atom):
    """Return a unique identifier for an Atom."""
    return atom.id_string()


# Default functions for node annotations
# - "return None" means that the attribute and value won't be included
#   to the output data, so that defaults of the JS library are used and files get smaller
# - A return of a value in some cases and None in other cases means that the
#   default value of the JS library is used in None cases and again files get smaller

def node_label_default(atom):
    # None => no node labels
    return '{} "{}"'.format(atom.type_name, atom.name) if atom.is_node() else atom.type_name


def node_color_default(atom):
    # None => black
    return 'red' if atom.is_node() else None


def node_opacity_default(atom):
    # None => 1.0
    return None


def node_size_default(atom):
    # None => 10
    return None


def node_shape_default(atom):
    # None => circle
    return 'rectangle' if atom.is_node() else None


def node_border_color_default(atom):
    # None => black
    return None


def node_border_size_default(atom):
    # None => 0.0
    return None


def node_label_color_default(atom):
    # None => black
    return None


def node_label_size_default(atom):
    # None => 12.0
    return None


def node_hover_default(atom):
    # None => no hover text
    return atom.short_string()


def node_click_default(atom):
    # None => no click text (in addition to always shown "Node: <id>" in header)
    return None


def node_image_default(atom):
    # None => no image inside node
    return None


def node_properties_default(atom):
    # None => no extra node annotations
    return None


def node_properties_tv(atom):
    return dict(mean=atom.tv.mean, confidence=atom.tv.confidence)


# Default functions for edge annotations

def edge_label_default(atom1, atom2):
    # None => no edge label
    return None


def edge_color_default(atom1, atom2):
    # None => black
    return None if atom1.is_link() and atom2.is_link() else 'red'


def edge_opacity_default(atom1, atom2):
    # None => 1.0
    return None


def edge_size_default(atom1, atom2):
    # None => 1.0
    return None


def edge_label_color_default(atom1, atom2):
    # None => black
    return None


def edge_label_size_default(atom1, atom2):
    # None => 8.0
    return None


def edge_hover_default(atom1, atom2):
    # None => no hover text
    return None


def edge_click_default(atom1, atom2):
    # None => no click text (in addition to always shown "Edge: <id>" in header)
    return None
