import networkx as _nx
from opencog.type_constructors import AtomSpace as _AtomSpace

from .args import check_arg as _check_arg
from .conversion import convert as _convert


GRAPHVIZ_METHODS = ['dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp']
NETWORKX_METHODS = [
    'bipartite', 'circular', 'kamada_kawai', 'planar', 'random', 'shell', 'spring',
    'spectral', 'spiral']
LAYOUT_METHODS = GRAPHVIZ_METHODS + NETWORKX_METHODS


def layout(data, method='neato', scale_x=1.0, scale_y=1.0, mirror_x=False, mirror_y=True,
           center_x=True, center_y=True, **kwargs):
    """Calculate a layout for a given NetworkX graph with a chosen method.

    Parameters
    ----------
    data : NetworkX Graph, NetworkX DiGraph, AtomSpace, list of Atoms
        Input that gets augmented by a layout in form of x and y coordinates for each node.

        If the data is an AtomSpace or list of Atoms, it is first converted to a
        NetworkX graph by implicitely calling :func:`convert` with default arguments.
        Alternatively, it can also be called explicitly by a user on an AtomSpace
        for finer control. The result can then be fed into this layout function.
    method : str
        Layout method for calculating node coordinates, e.g. a Graphviz layout engine.

        Possible values:

        - Graphviz layouts

            - ``"dot"``: hierarchical layout for directed graphs,
              see `dot <https://graphviz.org/docs/layouts/dot/>`__
            - ``"neato"``: spring model layout for up to 100 nodes,
              minimizes a global energy function,
              see `neato <https://graphviz.org/docs/layouts/neato/>`__
            - ``"twopi"``: radial layout placing nodes on concentric circles depending
              on their distance from a root node,
              see `twopi <https://graphviz.org/docs/layouts/twopi/>`__
            - ``"circo"``: circular layout,
              see `circo <https://graphviz.org/docs/layouts/circo/>`__
            - ``"fdp"``: spring model layout for larger graphs,
              reduces forces with the Fruchterman-Reingold heuristic,
              see `fdp <https://graphviz.org/docs/layouts/fdp/>`__
            - ``"sfdp"``: multiscale version of ``fdp`` for large graphs
              see `sfdp <https://graphviz.org/docs/layouts/sfdp/>`__

        - NetworkX layouts

            - ``bipartite``: nodes in two straight lines,
              see `bipartite_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.bipartite_layout.html>`__
            - ``circular``: nodes on a circle,
              see `circular_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.circular_layout.html>`__
            - ``kamada_kawai``: using Kamada-Kawai path-length cost-function,
              see `kamada_kawai_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html>`__
            - ``planar``: nodes without edge intersections, fails if the graph is not planar,
              see `planar_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.planar_layout.html>`__
            - ``random``: nodes uniformly at random in the unit square,
              see `random_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.random_layout.html>`__
            - ``shell``: nodes in concentric circles,
              best with ``nlist`` defining list of nodes for each shell,
              see `shell_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.shell_layout.html>`__
            - ``spectral``: using the eigenvectors of the graph Laplacian,
              see `spectral_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spectral_layout.html>`__
            - ``spiral``: nodes in a spiral,
              see `spiral_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spiral_layout.html>`__
            - ``spring``: using Fruchterman-Reingold force-directed algorithm,
              see `spring_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html>`__

    scale_x : int, float
        A number to contract or stretch the layout along the x coordinate.
    scale_y : int, float
        A number to contract or stretch the layout along the y coordinate.
    mirror_x : bool
        if ``True``, the x coordinates are inverted.
    mirror_y : bool
        if ``True``, the y coordinates are inverted.
    center_x : bool
        if ``True``, the x coordinates are shifted so the extreme values have equal distance to 0.
    center_y : bool
        if ``True``, the y coordinates are shifted so the extreme values have equal distance to 0.
    kwargs
        Other keyword arguments are forwarded to the layout method.

    Returns
    -------
    graph: NetworkX Graph or NetworkX DiGraph

    References
    ----------
    - Graphviz documentation:
      `layouts <https://graphviz.org/docs/layouts/>`__
    - NetworkX documentation:
      `graphviz_layout <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_agraph.graphviz_layout.html>`__

    Note
    ----
    Graphviz layouts are influenced by graph properties, e.g. whether a graph
    is directed or undirected, or whether the shapes of nodes are circle or rectangle.

    """
    # Argument processing
    _check_arg(data, 'data', (_nx.Graph, _nx.DiGraph, _AtomSpace, list))
    _check_arg(method, 'method', str, LAYOUT_METHODS)
    _check_arg(scale_x, 'scale_x', (int, float))
    _check_arg(scale_y, 'scale_y', (int, float))
    _check_arg(mirror_x, 'mirror_x', bool)
    _check_arg(mirror_y, 'mirror_y', bool)
    _check_arg(center_x, 'center_x', bool)
    _check_arg(center_y, 'center_y', bool)

    # Optional conversion
    if isinstance(data, (_AtomSpace, list)):
        data = _convert(data)

    # Calculate layout
    positions = calc_layout(data, method, kwargs)

    # Annotate graph
    data = annotate(data, positions, mirror_x, mirror_y, center_x, center_y, scale_x, scale_y)
    return data


def calc_layout(graph, method, kwargs):
    """Calculate x and y coordinates for each node in the given graph with the chosen method."""
    if method in GRAPHVIZ_METHODS:
        # Calculate a Graphviz layout
        pos = _nx.nx_agraph.graphviz_layout(graph, method, **kwargs)
    else:
        # Prepare a NetworkX layout
        function = getattr(_nx.drawing.layout, method + '_layout')
        if method == 'bipartite':
            kwargs = prepare_bipartite(graph, kwargs)
        elif method == 'shell':
            kwargs = prepare_shell(graph, kwargs)

        # Calculate a NetworkX layout
        pos = function(graph, **kwargs)

        # Pre-scale it to become roughly compatible with plotting without user-provided scaling
        pos = {node: (x*300, y*300) for node, (x, y) in pos.items()}
    return pos


def annotate(data, pos, mirror_x, mirror_y, center_x, center_y, scale_x, scale_y):
    """Annotate graph with coordinates from the layout and optional corrections."""
    nodes = data.nodes
    sign_x, sign_y = calc_mirror(mirror_x, mirror_y)
    shift_x, shift_y = calc_shift(pos, center_x, center_y)
    for uid, (x, y) in pos.items():
        node = nodes[uid]
        node['x'] = (x + shift_x) * scale_x * sign_x
        node['y'] = (y + shift_y) * scale_y * sign_y
    return data


def calc_mirror(mirror_x, mirror_y):
    sign_x = -1.0 if mirror_x else 1.0
    sign_y = -1.0 if mirror_y else 1.0
    return sign_x, sign_y


def calc_shift(layout, center_x, center_y):
    """Shift the x and/or y coordinates so they become centered around zero to improve plots."""
    if not center_x and not center_y:
        # Shift nothing
        shift_x = shift_y = 0.0  # shift nothing
    else:
        # Shift x and/or y
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for x, y in layout.values():
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        # Shift x or not
        if center_x and min_x != float('inf') and max_x != float('-inf'):
            shift_x = -min_x - (max_x - min_x) / 2.0
        else:
            shift_x = 0.0
        # Shift y or not
        if center_y and min_y != float('inf') and max_y != float('-inf'):
            shift_y = -min_y - (max_y - min_y) / 2.0
        else:
            shift_y = 0.0
    return shift_x, shift_y


def prepare_bipartite(graph, kwargs):
    """Add a default nodes argument based on color to get a plot with two lines of nodes."""
    try:
        all_colors = set(vals.get('color', None) for vals in graph.nodes.values())
        one_color = list(all_colors)[0]
        nodes_of_one_type = [key for key, vals in graph.nodes.items()
                             if vals.get('color', None) == one_color]
    except Exception:
        nodes_of_one_type = graph.nodes
    kwargs['nodes'] = kwargs.get('nodes', nodes_of_one_type)
    return kwargs


def prepare_shell(graph, kwargs):
    """Add a default nlist argument based on color to get a plot with two shells of nodes."""
    try:
        all_colors = set(vals.get('color', None) for vals in graph.nodes.values())
        one_color = list(all_colors)[0]
        nodes_of_one_type = [key for key, vals in graph.nodes.items()
                             if vals.get('color', None) == one_color]
        nodes_of_other_type = [key for key in graph.nodes if key not in nodes_of_one_type]
        nlist = [nodes_of_one_type, nodes_of_other_type]
    except Exception:
        nlist = [list(graph.nodes)]
    kwargs['nlist'] = kwargs.get('nlist', nlist)
    return kwargs
