from collections.abc import Callable as _Callable

from opencog.atomspace import Atom as _Atom
from opencog.type_constructors import AtomSpace as _AtomSpace

from .args import check_arg as _check_arg


FILTER_CONTEXTS = ['atom', 'in', 'out', 'both', 'in-tree', 'out-tree']


def filter(data, target, context='atom', mode='include'):
    """Apply a filter to an Atomspace or list of Atoms and return a list of selected Atoms.

    Parameters
    ----------
    data : Atomspace, list of Atoms
        The given Atomspace or list of Atoms that is filtered and thereby reduced to a
        shorter list of Atoms.
    target : str, int, Atom, list, Callable
        The targets that are selected by this filtering function.

        Possible types and their meaning:

        - ``str``: A string that is matched against ``.name`` and ``.type_name`` of each Atom.
          Capitalization is ignored.

          Examples:

          - ``target="andlink"`` will include all Atoms of type ``AndLink``.
          - ``target="$1"`` will include all Atoms with name ``"$1"``.

        - ``int``: An OpenCog Atom type that is matched against ``.type`` of each Atom.

          Examples:

          - ``target=opencog.atomspace.types.OrLink`` selects all Atoms of type ``OrLink``.

        - ``Atom``: An Atom that is used as it is.

          Examples:

          - ``target=list(atomspace)[4]`` selects the fifth Atom in the AtomSpace.

        - ``list``: A list of str, int and/or Atom. The types can be mixed freely.

          Examples:

          - ``target=["andlink", "OrLink"]`` selects all Atoms of type ``AndLink`` and ``OrLink``.
          - ``target=["notlink", "$1", opencog.atomspace.types.OrLink, list(atomspace)[4]]``
            selects all Atoms of type ``NotLink``, all Atoms with name ``"$1"``,
            all Atoms of type ``OrLink``, and the fifth Atom in the AtomSpace.

        - ``Callable``: A function that gets an Atom as input and needs to
          return ``True`` or ``False`` to indicate whether the Atom is selected or not.

          Examples:

          - ``target=lambda atom: atom.is_link()`` selects all Atoms that are Links
          - ``target=lambda atom: atom.name.startswith("$")`` selects all Atoms
            that have a name starting with ``$``.
    context : str, tuple
        The context of the selection of Atoms to which it shall be expanded.

        Possible values:

        - ``atom``: Only the Atoms specified by ``target`` are selected.
        - ``in``: The Atoms specified by ``target`` and
          all their incoming neighbors are selected.
        - ``out``: The Atoms specified by ``target`` and
          all their outgoing neighbors are selected.
        - ``both``: The Atoms specified by ``target`` and
          all their incoming and outgoing neighbors are selected.
          This is also known as
          `neighborhood <https://en.wikipedia.org/wiki/Neighbourhood_(graph_theory)>`__
          in graph theory or
          `egocentric network <https://research.library.gsu.edu/c.php?g=916490&p=6612505>`__
          in social network analysis.
        - ``in_tree``: The Atoms specified by ``target`` and all their incoming neighbors are
          selected, which is repeated until nothing can be added anymore.
          This is also known as
          `in-tree or anti-arborescence <https://en.wikipedia.org/wiki/Arborescence_(graph_theory)>`__
          in graph theory.
        - ``out_tree``: The Atoms specified by ``target`` and all their outgoing Atoms are
          selected, which is repeated until nothing can be added anymore.
          This is also known as
          `out-tree or arborescence <https://en.wikipedia.org/wiki/Arborescence_(graph_theory)>`__
          in graph theory.
        - ``(context, size)``: In the case of ``in``, ``out`` and ``both`` the context
          can come with a size, which means how often the selected Atoms are expanded in
          the chosen way.

          Examples:

          - ``("out", 2)`` means that the selected Atoms are expanded twice by their
            outgoing Atoms, instead of just once when using ``out``.
          - ``("in", 3)`` means that the selected Atoms are expanded thrice by their
            incoming Atoms, instead of just once when using ``in``.
          - ``("both", 2)`` means that the selected Atoms are expanded twice by their
            incoming and outgoing Atoms, instead of just once when using ``both``.
            Note that the result can be and usually is different than the combined
            results from ``("in", 2)`` and ``("out", 2)``, because adding an ingoing
            neighbor in step 1 and then its outgoing neighbors in step 2 (or vice versa)
            captures more Atoms.

    mode : str
        The selection of Atoms can be the result of the filtering, but it is also possible
        to exclude those Atoms and instead return all other ones.

        Possible values:

        - ``include``: The selection is included in the result.
        - ``exclude``: The selection is excluded from the result. Everything else is included.

    Returns
    -------
    atoms : list of Atoms

    Note
    ----
    Chaining is possible, which means that the output of a filter application can be used
    as input for another one. This allows to combine different targets, contexts and modes
    by performing a sequence of filtering steps. Example::

        import mevis as mv

        atomspace = mv.load('moses.scm')
        atoms = mv.filter(atomspace, target="AndLink", context="out-tree", mode="include")
        atoms = mv.filter(atoms, target="PredicateNode", context="atom", mode="exclude")
        mv.plot(atoms, 'vis', 'dot')

    The first line includes Atoms of type ``AndLink`` and their maximally expanded
    outgoing neighborhood. The second line excludes Atoms of type ``PredicateNode``
    from the previous result.

    """
    # Argument processing
    _check_arg(data, 'data', (list, _AtomSpace))
    _check_arg(target, 'target', (str, int, list, _Callable, _Atom))
    _check_arg(mode, 'mode', str, ['include', 'exclude'])
    if isinstance(context, tuple):
        context, size = context
        try:
            _check_arg(context, 'context', str, ['in', 'out', 'both'])
            _check_arg(size, 'size', int)
            if size < 0:
                raise ValueError('Context size needs to be equal to or greater than zero.')
        except Exception as excp:
            message = 'Argument "context" got an invalid tuple as value.'
            raise ValueError(message) from excp
    else:
        _check_arg(context, 'context', str, FILTER_CONTEXTS)
        size = 1
    given_atoms = data

    # Filter: Select all Atoms as specified by target
    if isinstance(target, _Atom):
        selected_atoms = [target]
    else:
        func = _prepare_filter_func(target)
        selected_atoms = [atom for atom in given_atoms if func(atom)]

    # Expand by context: if desired, include some neighboring atoms
    selected_atoms = _expand(selected_atoms, context, size)

    # Select by mode: if desired, invert the selected set of atoms (=exclude instead of include)
    atoms = _include_or_exclude(selected_atoms, given_atoms, mode)
    return atoms


def _prepare_filter_func(target):
    """Create a filter function depending on the type of the given target."""
    if isinstance(target, str):
        target = target.lower()

        def func(atom):
            # match: name, type name
            return atom.name.lower() == target \
                or atom.type_name.lower() == target
    elif isinstance(target, int):
        def func(atom):
            # match: type
            return int(atom.type) == target
    elif isinstance(target, list):
        target = set(x.lower() if isinstance(x, str) else x for x in target)

        def func(atom):
            # match: name, type name, type, atom
            return atom.type_name.lower() in target or \
                atom.name.lower() in target or \
                int(atom.type) in target or \
                atom in target
    elif isinstance(target, _Callable):
        func = target
    return func


def _expand(atoms, context, context_size):
    """Expand a list of atoms depending on the type of context that shall be included."""
    if context == 'in':
        # Add all Atoms in the incoming neighborhood of an Atom, repeat it if context size > 1
        for _ in range(context_size):
            expansion = set()
            for atom in atoms:
                expansion.add(atom)
                expansion.update(atom.incoming)
            atoms = list(expansion)
    elif context == 'out':
        # Add all Atoms in the outgoing neighborhood of an Atom, repeat it if context size > 1
        for _ in range(context_size):
            expansion = set()
            for atom in atoms:
                expansion.add(atom)
                expansion.update(atom.out)
            atoms = list(expansion)
    elif context == 'both':
        # Add all Atoms in the neighborhood of an Atom, repeat it if context size > 1
        for _ in range(context_size):
            expansion = set()
            for atom in atoms:
                expansion.add(atom)
                expansion.update(atom.incoming)
                expansion.update(atom.out)
            atoms = list(expansion)
    elif context == 'in-tree':
        # Add all Atoms in the incoming neighborhood of an Atom, repeat it until all is reached
        expansion = set()
        for atom in atoms:
            expansion = expansion.union(_dfs_in(atom))
        atoms = list(expansion)
    elif context == 'out-tree':
        # Add all Atoms in the outgoing neighborhood of an Atom, repeat it until all is reached
        expansion = set()
        for atom in atoms:
            expansion = expansion.union(_dfs_out(atom))
        atoms = list(expansion)
    return atoms


def _include_or_exclude(selected, given, mode):
    """Include or exclude the selected Atoms from the initially given Atoms."""
    if mode == 'exclude':
        selected = [atom for atom in given if atom not in selected]
    return selected


def _dfs_out(atom):
    """Traverse an Atom's outgoing neighborhood iteratively with a depth-first search."""
    atoms = [atom]
    stack = list(atom.out)
    while stack:
        atom = stack.pop(0)
        atoms.append(atom)
        stack[0:0] = atom.out
    return atoms


def _dfs_in(atom):
    """Traverse an Atom's incoming neighborhood iteratively with a depth-first search."""
    atoms = [atom]
    stack = list(atom.incoming)
    while stack:
        atom = stack.pop(0)
        atoms.append(atom)
        stack[0:0] = atom.incoming
    return atoms
