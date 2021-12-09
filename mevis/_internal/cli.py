import argparse
import ast
import os
import sys

from .conversion import convert as _convert
from .filtering import FILTER_CONTEXTS as _FILTER_CONTEXTS
from .filtering import filter as _filter
from .io import export as _export
from .io import load as _load
from .layouting import LAYOUT_METHODS as _LAYOUT_METHODS
from .layouting import layout as _layout
from .plotting import plot as _plot


def parse():
    """Serve as CLI entry point by parsing arguments and calling corresponding functions."""
    # Create parser
    parser = argparse.ArgumentParser(
        description='Visualize an OpenCog Atomspace as graph with two kinds of vertices.',
        formatter_class=argparse.RawTextHelpFormatter)

    # Add arguments
    parser.add_argument(
        '-i',
        metavar='input_filepath',
        required=True,
        type=validate_source,
        help='path of input file (.scm) containing an Atomspace')

    parser.add_argument(
        '-o',
        metavar='output_filepath',
        required=False,
        type=validate_target,
        help=('path of output file, with following cases'
              '\n- none     create plot and display it in webbrowser'
              '\n- .html    create plot and export it to a HTML file'
              '\n- .jpg     create plot and export it to a JPG file'
              '\n- .png     create plot and export it to a PNG file'
              '\n- .svg     create plot and export it to a SVG file'
              '\n           works only with backend d3'
              '\n- .gml     create graph and export it to GML file'
              '\n- .gml.gz  same but file is compressed with gzip'
              '\n- .gml.bz2 same but file is compressed with bzip2'))

    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='overwrite output_filepath if it already exists')

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='print messages about intermediary results')

    parser.add_argument(
        '-b',
        metavar='backend',
        required=False,
        type=str,
        choices=('d3', 'vis', 'three'),
        default='vis',
        help='backend library for graph visualization'
             '\n"d3" = d3.js'
             '\n"vis" = vis-network.js'
             '\n"three" = 3d-force-directed.js using three.js')

    parser.add_argument(
        '-l',
        metavar='layout_method',
        required=False,
        type=str,
        choices=_LAYOUT_METHODS,
        help='layout method to calculate node coordinates\n{}'.format(
            '\n'.join('- "{}"'.format(method) for method in _LAYOUT_METHODS)))

    parser.add_argument(
        '-cd',
        metavar='capture_delay',
        required=False,
        type=float,
        default=3.5,
        help='delay in seconds when capturing a static image'
             '\nfor JPG/PNG/SVG export. Default: 3.5')

    parser.add_argument(
        '-ft',
        metavar='filter_target',
        required=False,
        type=str,
        default=None,
        help='filter target to select Atoms')

    parser.add_argument(
        '-fc',
        metavar='filter_context',
        required=False,
        type=validate_context,
        default='atom',
        help='filter context to expaned selected atoms to'
             '\n- "atom" = selected Atoms'
             '\n- "in" = selection + incoming neighbors'
             '\n- "out" = selection + outgoing neighbors'
             '\n- "both" = selection + incoming and outgoing'
             '\n  neighbors'
             '\n- "in-tree" = selection + repeated incoming'
             '\n  neighbors'
             '\n- "out-tree" = selection + repeated outgoing'
             '\n  neighbors'
             '''\n- "('in', n)" = selection + incoming neighbors'''
             '\n  within distance n'''
             '''\n- "('out', n)" = selection + outgoing neighbors'''
             '\n  within distance n'''
             '''\n- "('both', n)" = selection + incoming and outgoing'''
             '\n  neighbors within distance n')

    parser.add_argument(
        '-fm',
        metavar='filter_mode',
        required=False,
        type=str,
        choices=('include', 'exclude'),
        default='include',
        help='filter mode deciding how to use the selection'
             '\n- "include" = include selected Atoms to output'
             '\n- "exclude" = exclude selected Atoms from output')

    parser.add_argument(
        '-gua',
        action='store_true',
        help='graph is unannotated, no properties are added')

    parser.add_argument(
        '-gud',
        action='store_true',
        help='graph is undirected, no arrows are drawn')

    parser.add_argument(
        '-nl', metavar='node_label',
        help='text shown below node', required=False, type=str)
    parser.add_argument('-nc', metavar='node_color', required=False, type=str)
    parser.add_argument('-no', metavar='node_opacity', required=False, type=str)
    parser.add_argument('-ns', metavar='node_size', required=False, type=str)
    parser.add_argument('-nsh', metavar='node_shape', required=False, type=str)
    parser.add_argument('-nbc', metavar='node_border_color', required=False, type=str)
    parser.add_argument('-nbs', metavar='node_border_size', required=False, type=str)
    parser.add_argument('-nlc', metavar='node_label_color', required=False, type=str)
    parser.add_argument('-nls', metavar='node_label_size', required=False, type=str)
    parser.add_argument(
        '-nh', metavar='node_hover',
        help='text shown when hovering with mouse over a node', required=False, type=str)
    parser.add_argument(
        '-ncl', metavar='node_click',
        help='text shown in div below plot when clicking on a node', required=False, type=str)
    parser.add_argument(
        '-ni', metavar='node_image',
        help='image drawn inside node, URL or data URL', required=False, type=str)
    parser.add_argument(
        '-np', metavar='node_properties',
        help='other annotations for a node given as key/val dict', required=False, type=str)

    parser.add_argument(
        '-el', metavar='edge_label',
        help='text shown in midpoint of edge', required=False, type=str)
    parser.add_argument('-ec', metavar='edge_color', required=False, type=str)
    parser.add_argument('-eo', metavar='edge_opacity', required=False, type=str)
    parser.add_argument('-es', metavar='edge_size', required=False, type=str)
    parser.add_argument('-elc', metavar='edge_label_color', required=False, type=str)
    parser.add_argument('-els', metavar='edge_label_size', required=False, type=str)
    parser.add_argument(
        '-eh', metavar='edge_hover',
        help='text shown when hovering with mouse over an edge', required=False, type=str)
    parser.add_argument(
        '-ecl', metavar='edge_click',
        help='text shown in div below plot when clicking on an edge', required=False, type=str)

    parser.add_argument(
        '--kwargs', help='optional keyword arguments forwarded to plot function', nargs='*',
        action=KwargsParser)

    # Parse
    args = parser.parse_args()
    source = args.i
    target = args.o
    backend = args.b
    layout = args.l
    capture_delay = args.cd
    overwrite = args.force
    verbose = args.verbose

    filter_target = try_eval(args.ft)
    filter_context = args.fc
    filter_mode = args.fm

    graph_annotated = not args.gua
    graph_directed = not args.gud

    node_label = try_eval(args.nl)
    node_color = try_eval(args.nc)
    node_opacity = try_eval(args.no)
    node_size = try_eval(args.ns)
    node_shape = try_eval(args.nsh)
    node_border_color = try_eval(args.nbc)
    node_border_size = try_eval(args.nbs)
    node_label_color = try_eval(args.nlc)
    node_label_size = try_eval(args.nls)
    node_hover = try_eval(args.nh)
    node_click = try_eval(args.ncl)
    node_image = try_eval(args.ni)
    node_properties = try_eval(args.np)

    edge_label = try_eval(args.el)
    edge_color = try_eval(args.ec)
    edge_opacity = try_eval(args.eo)
    edge_size = try_eval(args.es)
    edge_label_color = try_eval(args.elc)
    edge_label_size = try_eval(args.els)
    edge_hover = try_eval(args.eh)
    edge_click = try_eval(args.ecl)

    kwargs = dict() if args.kwargs is None else args.kwargs

    # Collect
    filt_args = [filter_target, filter_context, filter_mode]
    conv_args = [
        graph_annotated, graph_directed, node_label, node_color, node_opacity, node_size,
        node_shape, node_border_color, node_border_size, node_label_color, node_label_size,
        node_hover, node_click, node_image, node_properties,
        edge_label, edge_color, edge_opacity, edge_size, edge_label_color, edge_label_size,
        edge_hover, edge_click]

    # Mutually dependent checks
    if (not overwrite) and (target is not None) and os.path.exists(target):
        sys.tracebacklimit = 0
        message = (
            'The provided output_filepath "{}" already exists. '
            'You can use --force to overwrite it.'.format(target))
        raise argparse.ArgumentTypeError(message) from None

    # Perform the actions required by the arguments
    perform_it(
        source, target, overwrite, verbose, backend, layout, capture_delay, filt_args,
        conv_args, kwargs)


def validate_source(filepath):
    """Check if the given source filepath exists."""
    if not os.path.exists(filepath):
        message = 'The source filepath "{}" does not exist.'.format(filepath)
        raise argparse.ArgumentTypeError(message)
    return filepath


def validate_target(filepath):
    """Check if the given target filepath ends in a known format."""
    known_formats = ['.html', '.jpg', '.png', '.svg', '.gml', '.gml.gz', '.gml.bz2']
    if not any(filepath.endswith(x) for x in known_formats):
        message = 'The target filepath needs to end with one of {}'.format(
            ', '.join('"{}"'.format(x) for x in known_formats))
        raise argparse.ArgumentTypeError(message)
    return filepath


def validate_context(context):
    """Check if the given filter context is a know string or valid tuple."""
    if context not in _FILTER_CONTEXTS:
        try:
            # Try to convert the command line string into a tuple of form (str, int)
            context = ast.literal_eval(context)
            assert isinstance(context, tuple)
            assert context[0] in ('in', 'out', 'both')
            assert isinstance(context[1], int)
            assert context[1] >= 0
        except Exception:
            message = (
                'filter_context needs to be either a string from {} or'
                """from "('in', 2)", "('out', 2)", "('both', 2)" where """
                '2 may be replaced by any integer '
                '>= 0.'.format(', '.join('"{}"'.format(s) for s in _FILTER_CONTEXTS)))
            raise argparse.ArgumentTypeError(message)
    return context


class KwargsParser(argparse.Action):
    """Parse optional keyword arguments and put them into a dictionary.

    References:
    - https://sumit-ghosh.com/articles/parsing-dictionary-key-value-pairs-kwargs-argparse-python

    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            try:
                value = ast.literal_eval(value)
            except Exception:
                pass
            getattr(namespace, self.dest)[key] = value
        if len(getattr(namespace, self.dest)) == 0:
            raise ValueError('Argument "kwargs" got no entries.')


def try_eval(expr):
    """Try to evaluate a given expression as Python code, e.g. for lists or lambda functions."""
    if expr is not None:
        try:
            expr = eval(expr)  # dangerous, but ast_eval does not work for lambda functions
        except Exception:
            expr = str(expr)
    return expr


def perform_it(source, target, overwrite, verbose, backend, layout, capture_delay, filt_args,
               conv_args, kwargs):
    """Perform the actions that were requested from the CLI."""
    # Load
    atomspace = load_atomspace(source, verbose)

    # Optional: Filter
    atoms = filter_atomspace(atomspace, filt_args, verbose)

    # Convert
    graph = convert_atomspace_to_graph(atoms, conv_args, verbose)

    # Optional: Layout
    graph = layout_graph(graph, layout, verbose)

    # Plot or export
    if target is None or any(target.endswith(ext) for ext in ('html', 'jpg', 'png', 'svg')):
        plot_graph(graph, target, backend, verbose, overwrite, capture_delay, kwargs)
    else:
        export_graph(graph, target, verbose, overwrite)


def load_atomspace(source, verbose):
    """Load an Atomspace from a file with print message."""
    printv('Importing an Atomspace from file "{}".'.format(source), verbose)
    atomspace = _load(source)
    printv('Done. It contains {} Atoms.'.format(atomspace.size()), verbose)
    printv('', verbose)
    return atomspace


def filter_atomspace(atoms, filter_args, verbose):
    """Filter the AtomSpace and optionally print status messages."""
    if filter_args[0] is not None:
        printv('Filtering the AtomSpace', verbose)
        atoms = _filter(atoms, *filter_args)
        printv('Done. It contains {} remaining Atoms.'.format(len(atoms)), verbose)
        printv('', verbose)
    return atoms


def convert_atomspace_to_graph(atoms, convert_args, verbose):
    """Convert the AtomSpace and optionally print status messages."""
    printv('Converting the AtomSpace to a graph', verbose)
    graph = _convert(atoms, *convert_args)
    printv('Done. It contains {} vertices and {} edges.'.format(
        len(graph.nodes), len(graph.edges)), verbose)
    printv('', verbose)
    return graph


def layout_graph(graph, layout, verbose):
    """Calculate a graph layout and optionally print status messages."""
    if layout is not None:
        printv('Calculating a layout with "{}".'.format(layout), verbose)
        graph = _layout(graph, layout)
        printv('Done.', verbose)
        printv('', verbose)
    return graph


def plot_graph(graph, target, backend, verbose, overwrite, capture_delay, kwargs):
    """Plot the graph, display it or export it as HTML file, optionally print status messages."""
    fig = _plot(graph, backend, **kwargs)
    if target is None:
        fig.display()
    elif target.endswith('html'):
        printv('Storing a visualization as HTML file to "{}". '.format(target), verbose)
        fig.export_html(target, overwrite)
        printv('Done. It has a file size of {} bytes.'.format(get_filesize(target)), verbose)
    elif target.endswith('jpg'):
        printv('Storing a visualization as JPG file to "{}". '.format(target), verbose)
        fig.export_jpg(target, overwrite, capture_delay=capture_delay)
        printv('Done. It has a file size of {} bytes.'.format(get_filesize(target)), verbose)
    elif target.endswith('png'):
        printv('Storing a visualization as PNG file to "{}". '.format(target), verbose)
        fig.export_png(target, overwrite, capture_delay=capture_delay)
        printv('Done. It has a file size of {} bytes.'.format(get_filesize(target)), verbose)
    elif target.endswith('svg'):
        printv('Storing a visualization as SVG file to "{}". '.format(target), verbose)
        fig.export_svg(target, overwrite, capture_delay=capture_delay)
        printv('Done. It has a file size of {} bytes.'.format(get_filesize(target)), verbose)


def export_graph(graph, target, verbose, overwrite):
    """Export the graph as GML file and optionally print status messages."""
    printv('Storing a GML graph representation to "{}".'.format(target), verbose)
    _export(graph, target, overwrite=overwrite)
    printv('Done. It has a file size of {} bytes.'.format(get_filesize(target)), verbose)


def printv(message, verbose):
    """Print or ignore the given message."""
    if verbose:
        print(message)


def get_filesize(filepath):
    """Get the size of a file in bytes."""
    return os.path.getsize(filepath)
