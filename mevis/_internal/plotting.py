from collections.abc import Callable as _Callable

import gravis as _gv
import networkx as _nx
from opencog.atomspace import Atom as _Atom
from opencog.type_constructors import AtomSpace as _AtomSpace

from .args import check_arg as _check_arg
from .conversion import convert as _convert
from .filtering import filter as _filter
from .layouting import LAYOUT_METHODS as _LAYOUT_METHODS
from .layouting import layout as _layout


def plot(data, backend='vis',
         layout_method=None, layout_scale_x=1.0, layout_scale_y=1.0,
         layout_mirror_x=False, layout_mirror_y=True, layout_center_x=True, layout_center_y=True,
         filter_target=None, filter_context='atom', filter_mode='include',
         graph_annotated=True, graph_directed=True, node_label=None, node_color=None,
         node_opacity=None, node_size=None, node_shape=None, node_border_color=None,
         node_border_size=None, node_label_color=None, node_label_size=None, node_hover=None,
         node_click=None, node_image=None, node_properties=None,
         edge_label=None, edge_color=None, edge_opacity=None, edge_size=None,
         edge_label_color=None, edge_label_size=None, edge_hover=None, edge_click=None,
         **kwargs):
    """Create a graph visualization of a given AtomSpace, list of Atoms or NetworkX graph.

    Parameters
    ----------
    data : Atomspace, list of Atoms, NetworkX Graph, NetworkX DiGraph
        The input data that shall be visualized.
        If it is already a NetworkX Graph or NetworkX DiGraph, no conversion,
        layouting and filtering steps are performed, which means that most
        arguments have no effect.
    backend : str
        Library used for the graph visualization.

        Possible values:

        - ``"d3"``: Uses `d3.js <https://d3js.org/>`__
          to generate a 2d plot based on the
          `HTML SVG element <https://developer.mozilla.org/en-US/docs/Web/SVG/Element/svg>`__,
          which is vector graphics that can be exported as SVG, PNG or JPG.
        - ``"vis"``: Uses `vis.js <https://visjs.org/>`__
          to generate a 2d plot based on the
          `HTML Canvas element <https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API>`__,
          which is raster graphics that can be exported as PNG or JPG.
        - ``"three"``: Uses `three.js <https://threejs.org/>`__
          to generate a 3d plot based on
          `HTML WebGL element <https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API>`__,
          which is raster graphics that can be exported as PNG or JPG.
    filter_[...]
        See documentation of the :func:`filter` function.
    graph_[...], node_[...], edge_[...]
        See documentation of the :func:`convert` function.
    layout_[...]
        See documentation of the :func:`layout` function.
    kwargs
        Other keyword arguments are forwarded to the plotting method.
        See documentation of
        `gravis <https://robert-haas.github.io/gravis-docs/>`__.
        Various aspects of the graph visualizations can be changed interactively
        by a user in the HTML menus, but often it is desirable to set suitable
        initial values, e.g. ``edge_curvature=0.2`` for curved instead of
        straight edges.

    Returns
    -------
    fig : `Figure <https://robert-haas.github.io/gravis-docs/rst/api/figure.html>`__
        A figure object from gravis that can be used for displaying or exporting the plot.

    Note
    ----
    **Pre-processing steps** can be triggered by providing values for
    the arguments ``filter_target`` or ``layout_method`` and modified
    by providing values for arguments like ``node_color`` and ``node_size``.

    1. **Filter**: Reduce the AtomSpace to a list of relevant Atoms.
    2. **Convert**: Transform the AtomSpace to a NetworkX graph and add annotations
       to its nodes and edges. By providing arguments like ``node_size`` it is possible
       to translate information such as truth values into visual properties such as
       node size, color or shape.
    3. **Layout**: Calculate x and y coordinates to better recognize structures
       in the AtomSpace such as hierarchies and clusters.

    These steps are implemented by the functions
    :func:`filter`, :func:`convert` and :func:`layout`.
    They are called implicitely by this plotting function with default arguments.
    Alternatively, they can be called explicitly by a user on an AtomSpace
    for finer control. The result can then be fed into this plotting function.

    """
    # Argument processing
    _check_arg(data, 'data', (_AtomSpace, list, _nx.Graph, _nx.DiGraph))
    _check_arg(backend, 'backend', str, ['d3', 'vis', 'three'])
    # layout
    _check_arg(layout_method, 'layout_method', str, _LAYOUT_METHODS, allow_none=True)
    _check_arg(layout_scale_x, 'layout_scale_x', (int, float))
    _check_arg(layout_scale_x, 'layout_scale_y', (int, float))
    _check_arg(layout_mirror_x, 'layout_mirror_x', bool)
    _check_arg(layout_mirror_y, 'layout_mirror_y', bool)
    _check_arg(layout_center_x, 'layout_center_x', bool)
    _check_arg(layout_center_y, 'layout_center_y', bool)
    # filter
    _check_arg(
        filter_target, 'filter_target', (str, int, list, _Callable, _Atom), allow_none=True)
    _check_arg(filter_context, 'filter_context', (str, tuple))
    _check_arg(filter_mode, 'filter_mode', str, ['include', 'exclude'])
    # convert: arguments have exactly the same name and thus are checked in the convert function

    # Preparing the graph or AtomSpace
    if isinstance(data, (_nx.Graph, _nx.DiGraph)):
        graph = data
    else:
        # Optional: Filtering of AtomSpace
        if filter_target is None:
            atoms = data
        else:
            atoms = _filter(data, filter_target, filter_context, filter_mode)

        # Conversion of AtomSpace to graph
        graph = _convert(
            atoms, graph_annotated, graph_directed,
            node_label, node_color, node_opacity, node_size, node_shape,
            node_border_color, node_border_size,
            node_label_color, node_label_size, node_hover, node_click,
            node_image, node_properties,
            edge_label, edge_color, edge_opacity, edge_size,
            edge_label_color, edge_label_size, edge_hover, edge_click)

        # Optional: Layout of graph
        if layout_method is not None:
            graph = _layout(
                graph, layout_method,
                layout_scale_x, layout_scale_y, layout_mirror_x, layout_mirror_y,
                layout_center_x, layout_center_y)

    # Setting some defaults for plotting
    kwargs['node_label_data_source'] = kwargs.get('node_label_data_source', 'label')
    kwargs['edge_label_data_source'] = kwargs.get('edge_label_data_source', 'label')
    kwargs['show_edge_label'] = kwargs.get('show_edge_label', edge_label is not None)

    # Plotting
    if backend == 'd3':
        fig = _gv.d3(graph, **kwargs)
    elif backend == 'vis':
        fig = _gv.vis(graph, **kwargs)
    elif backend == 'three':
        fig = _gv.three(graph, **kwargs)
    return fig
