import errno as _errno
import os as _os

import networkx as _nx
from opencog.atomspace import AtomSpace as _AtomSpace
from opencog.scheme import scheme_eval as _scheme_eval
from opencog.utilities import load_file as _load_file
from opencog.utilities import set_default_atomspace as _set_default_atomspace

from .args import check_arg as _check_arg


def create(set_as_default=True):
    """Create an empty AtomSpace and set it as default.

    Parameters
    ----------
    set_as_default : bool
        If ``True``, the newly created AtomSpace is set as default in OpenCog.

    References
    ----------
    - OpenCog Wiki: `Python <https://wiki.opencog.org/w/Python>`__

    Returns
    -------
    atomspace : AtomSpace

    """
    atomspace = _AtomSpace()
    if set_as_default:
        _set_default_atomspace(atomspace)
    return atomspace


def load(filepath, method='primitive', verbose=False):
    """Load an Atomspace from a given filepath with a chosen method.

    Parameters
    ----------
    filepath : str
        Path of a text file that contains Atomese code.
    method : str
        Possible values:

        - ``"basic"``: uses Scheme code ``(load "data.scm")``
        - ``"primitive"``: uses Scheme code ``(primitive-load "data.scm")``
        - ``"fast"``: uses Scheme code ``(load-file "data.scm")``
        - ``"python"``: uses Python function ``opencog.utilities.load_file``
    verbose : bool
        if ``True``, a short message is printed about the AtomSpace that was loaded.

    References
    ----------
    - AtomSpace example: `persist-file.scm
      <https://github.com/opencog/atomspace/blob/master/examples/atomspace/persist-file.scm>`__

    Returns
    -------
    atomspace : AtomSpace

    """
    # Argument processing
    _check_arg(filepath, 'filepath', str)
    _check_arg(method, 'method', str, ['basic', 'primitive', 'fast', 'python'])
    _check_arg(verbose, 'verbose', bool)
    if not _os.path.isfile(filepath):
        raise FileNotFoundError(_errno.ENOENT, _os.strerror(_errno.ENOENT), filepath)

    # Create Atomspace and load modules
    atomspace = _AtomSpace()
    _load_all_modules(atomspace)

    # Import from file
    if method == 'basic':
        _scheme_eval(atomspace, '(load "{}")'.format(filepath))
    elif method == 'primitive':
        _scheme_eval(atomspace, '(primitive-load "{}")'.format(filepath))
    elif method == 'fast':
        _try_scheme_eval(atomspace, '(use-modules (opencog persist-file))')
        _scheme_eval(atomspace, '(load-file "{}")'.format(filepath))
    elif method == 'python':
        _load_file(filepath, atomspace)

    # Report
    if verbose:
        print('Imported an Atomspace with {} Atoms from filepath "{}".'.format(
            atomspace.size(), filepath))
    return atomspace


def store(atomspace, filepath, method='basic', verbose=False, overwrite=False):
    """Store an Atomspace to a given filepath with a chosen method.

    Parameters
    ----------
    filepath : str
        Path of a text file that contains Atomese code.
    method : str
        Possible values:

        - ``basic``: uses Scheme code ``(export-all-atoms "data.scm")``
        - ``file-storage-node``: uses Scheme code ``(define fsn (FileStorageNode "data.scm"))``

          Caution: This command adds a new ``FileStorageNode`` to the AtomSpace,
          which will also appear in the exported file.
    verbose : bool
        if ``True``, a short message is printed about the AtomSpace that was loaded.
    overwrite : bool
        If False, a ``FileExistsError`` will be raised in case there is already a
        file with the given filepath. if ``True``, the file will be overwritten.

    References
    ----------
    - AtomSpace example: `persist-file.scm
      <https://github.com/opencog/atomspace/blob/master/examples/atomspace/persist-file.scm>`__
    - OpenCog Wiki: `StorageNode
      <https://wiki.opencog.org/w/StorageNode>`__

    """
    # Argument processing
    _check_arg(filepath, 'filepath', str)
    _check_arg(method, 'method', str, ['basic', 'file-storage-node'])
    _check_arg(verbose, 'verbose', bool)

    # Checks
    if not overwrite:
        check_if_file_exists(filepath)

    # Load modules
    _load_storage_modules(atomspace)

    # Export to file
    if method == 'basic':
        _scheme_eval(atomspace, '(export-all-atoms "{}")'.format(filepath))
    elif method == 'file-storage-node':
        _scheme_eval(atomspace, '(define fsn (FileStorageNode "{}"))'.format(filepath))
        _scheme_eval(atomspace, '(cog-open fsn)')
        _scheme_eval(atomspace, '(store-atomspace fsn)')
        _scheme_eval(atomspace, '(cog-close fsn)')

    # Report
    if verbose:
        print('Exported an Atomspace with {} Atoms to filepath "{}".'.format(
            atomspace.size(), filepath))


def export(graph, filepath, overwrite=False):
    """Export a NetworkX graph in a chosen format.

    Parameters
    ----------
    graph : NetworkX Graph, NetworkX DiGraph
    filepath : str

        Possible file extensions:

        - ``gml``: Export the graph as
          `Graph Modeling Language (GML)
          <https://en.wikipedia.org/wiki/Graph_Modelling_Language>`__ file.
        - ``gml.gz``: Export the graph as GML file compressed with
          `gzip <https://en.wikipedia.org/wiki/Gzip>`__.
        - ``gml.bz2``: Export the graph as GML file compressed with
          `bzip2 <https://en.wikipedia.org/wiki/Bzip2>`__. It takes longer than gzip
          but produces a bit smaller files.

    References
    ----------
    - NetworkX documentation: `networkx.readwrite.gml.write_gml
      <https://networkx.org/documentation/stable/reference/readwrite/generated/networkx.readwrite.gml.write_gml.html>`__

    """
    # Argument processing
    _check_arg(graph, 'graph', (_nx.Graph, _nx.DiGraph))
    _check_arg(filepath, 'filepath', str)
    _check_arg(overwrite, 'overwrite', bool)

    # Checks
    known_formats = ['gml', 'gml.gz', 'gml.bz2']
    if not any(filepath.endswith(x) for x in known_formats):
        message = 'The filepath "{}" does not end in any known format: {}'.format(
            filepath, ', '.join(known_formats))
        raise ValueError(message)
    if not overwrite:
        check_if_file_exists(filepath)

    # Export
    _nx.readwrite.gml.write_gml(graph, filepath)


def _try_scheme_eval(atomspace, code):
    """Try to run a given Scheme code fragment and ignore any RuntimeError."""
    try:
        _scheme_eval(atomspace, code)
    except RuntimeError:
        pass


def _load_all_modules(atomspace):
    """Load OpenCog modules that are often used and cleanup the Atomspace.

    References
    ----------
    - https://github.com/opencog/agi-bio/tree/master/bioscience
    - https://github.com/opencog/rocca/blob/master/rocca/agents/core.py

    """
    cmds = (
        '(use-modules (opencog))',
        '(use-modules (opencog persist))',
        '(use-modules (opencog persist-file))',
        '(use-modules (opencog bioscience))',
        '(use-modules (opencog spacetime))',
        '(use-modules (opencog miner))',
        '(use-modules (opencog pln))',
    )
    for cmd in cmds:
        _try_scheme_eval(atomspace, cmd)

    # Remove Atoms, e.g. miner introduces three (LambdaLink, PresentLink, VariableNode)
    atomspace.clear()


def _load_storage_modules(atomspace):
    """Load OpenCog modules that might be required for storing an Atomspace to a file."""
    cmds = (
        '(use-modules (opencog))',
        '(use-modules (opencog persist))',
        '(use-modules (opencog persist-file))',
    )
    for cmd in cmds:
        _try_scheme_eval(atomspace, cmd)


def check_if_file_exists(filepath):
    """Check if a filepath already exists.

    Raises
    ------
    FileExistsError : Raised if there is a file at the given filepath.

    """
    if _os.path.isfile(filepath):
        raise FileExistsError(_errno.EEXIST, _os.strerror(_errno.EEXIST), filepath)
