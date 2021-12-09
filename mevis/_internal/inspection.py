import networkx as _nx
from opencog.type_constructors import AtomSpace as _AtomSpace

from .args import check_arg as _check_arg


def inspect(data, count_details=True):
    """Inspect an AtomSpace or graph by counting elements.

    Parameters
    ----------
    data : AtomSpace, list of Atoms, NetworkX Graph, NetworkX DiGraph
    count_details : bool
        If ``True``, some detailed properties of the AtomSpace or Graph are counted.

    Returns
    -------
    counts : dict
        A dictionary of element/count pairs.

        - If AtomSpace or list of Atoms:
          A dictionary that contains counts of Atoms, Nodes, Links
          and another dictionary with counts for each Atom type.
        - If NetworkX Graph or NetworkX DiGraph:
          A dictionary that contains counts of nodes, edges and annotations.

    """
    # Argument processing
    _check_arg(data, 'data', (list, _AtomSpace, _nx.Graph, _nx.DiGraph))

    # Inspection
    if isinstance(data, (list, _AtomSpace)):
        stats = inspect_atomspace(data, count_details)
    else:
        stats = inspect_graph(data, count_details)
    return stats


def inspect_atomspace(data, count_details):
    if count_details:
        # Count
        num_nodes = 0
        num_links = 0
        num_types = dict()
        for atom in data:
            if atom.is_node():
                num_nodes += 1
            else:
                num_links += 1
            key = atom.type_name
            try:
                num_types[key] += 1
            except KeyError:
                num_types[key] = 1
        # Combine
        stats = dict(
            atoms=num_nodes+num_links,
            nodes=num_nodes,
            links=num_links,
            types=num_types,
        )
    else:
        # Count
        num_nodes = 0
        num_links = 0
        for atom in data:
            if atom.is_node():
                num_nodes += 1
            else:
                num_links += 1
        # Combine
        stats = dict(
            atoms=num_nodes+num_links,
            nodes=num_nodes,
            links=num_links,
        )
    return stats


def inspect_graph(data, count_details):
    if count_details:
        # Count
        num_nodes = len(data.nodes)
        num_edges = len(data.edges)
        node_cnt = dict()
        for name in data.nodes:
            for key, val in data.nodes[name].items():
                try:
                    node_cnt[key].add(val)
                except KeyError:
                    node_cnt[key] = set([val])
        for key in node_cnt:
            node_cnt[key] = len(node_cnt[key])
        edge_cnt = dict()
        for n1, n2 in data.edges:
            for key, val in data.edges[n1, n2].items():
                try:
                    edge_cnt[key].add(val)
                except KeyError:
                    edge_cnt[key] = set([val])
        for key in edge_cnt:
            edge_cnt[key] = len(edge_cnt[key])
        # Combine
        stats = dict(
            nodes=num_nodes,
            edges=num_edges,
            node_properties=node_cnt,
            edge_properties=edge_cnt,
        )
    else:
        # Count
        num_nodes = len(data.nodes)
        num_edges = len(data.edges)
        # Combine
        stats = dict(
            nodes=num_nodes,
            edges=num_edges,
        )
    return stats
