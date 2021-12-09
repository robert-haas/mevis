"""This is the package :mod:`mevis`.

Its main purpose is to provide interactive AtomSpace visualizations
for the OpenCog project. Beyond that it comes with some inspection,
filtering, conversion, layouting and I/O capabilities.

"""

__all__ = [
    'convert',
    'create',
    'export',
    'filter',
    'inspect',
    'layout',
    'load',
    'plot',
    'store',
]

__version__ = '0.1.0'


from ._internal import convert, create, export, filter, inspect, layout, load, plot, store
