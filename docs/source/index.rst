mevis
#####

Welcome! You have found the documentation of the Python 3 package
:doc:`mevis <rst/package_references>`.



What is this package?
=====================

Its name stands for metagraph visualization and its purpose is to support the
`OpenCog project <https://opencog.org/>`__
with some additional filtering, conversion, layouting and plotting capabilities.
OpenCog uses a knowledge representation called
`AtomSpace <https://wiki.opencog.org/w/AtomSpace>`__, which is
named after
`atomic formulae <https://en.wikipedia.org/wiki/Atomic_formula>`__
in logic. In mathematical terms an AtomSpace is a generalized hypergraph, also referred
to as metagraph. The following lists some relationships between graphs, hypergraphs
and metagraphs that allow AtomSpaces to be transformed to graphs and then plotted
with existing graph visualization methods such as those provided by
`gravis <https://robert-haas.github.io/gravis-docs/>`__, which this package builds upon.

- A `graph <https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)>`__
  consists of vertices and edges, also known as nodes and links.
  Each edge can connect exactly two vertices.
- A `hypergraph <https://en.wikipedia.org/wiki/Hypergraph>`__
  consists of vertices and generalized edges or hyperedges.
  Each hyperedge can connect an arbitrary number of vertices.
- A `metagraph <https://arxiv.org/abs/2102.10581>`__
  consists of vertices and generalized hyperedges. Each generalized hyperedge
  can connect an arbitrary number of vertices but may also point to
  other edges and by transitivity to entire subgraphs.
- A hypergraph can be converted to an equivalent
  `bipartite graph <https://en.wikipedia.org/wiki/Bipartite_graph>`__,
  which is a graph with two disjoint and independent sets of vertices,
  one representing the original vertices and the other representing the hyperedges.
- A metagraph can be converted in a similar fashion, but the resulting graph
  is not bipartite, because the two disjoint sets of vertices are not 
  `independent <https://en.wikipedia.org/wiki/Independent_set_(graph_theory)>`__,
  since edges may connect vertices of the same kind.

OpenCog uses a metagraph to enable the integration of various data sources
into one knowledge representation. This allows different machine learning and
reasoning algorithms to operate together on a shared ground, with the aim to
overcome their individual bottlenecks by cooperation and achievement of
`cognitive synergy <https://arxiv.org/abs/1703.04361>`__.
For further background information, there are
accessible explanations of these concepts in interviews with
`Ben Goertzel <https://www.goertzel.org>`__
on the
`Lex Fridman podcast <https://www.youtube.com/watch?v=OpSmCKe27WE&t=5872s>`__
and
`Towards Data Science podcast <https://youtu.be/-VKF1lJhspg?t=2725>`__,
as well as an in-depth
`article <https://wiki.opencog.org/wikihome/images/c/cc/Ram-cpu.pdf>`__
by
`Linas Vepstas <https://linas.org/>`__
that motivates the use of a metagraph representation in detail.
Beyond that, there are numerous articles on the
`OpenCog Wiki <https://wiki.opencog.org>`__
and academic publications by
`Ben Goertzel <https://arxiv.org/search/cs?searchtype=author&query=Goertzel%2C+B>`__,
`Linas Vepstas <https://arxiv.org/search/?searchtype=author&query=Vepstas%2C+L>`__
and their colleagues. There are also recorded talks that were given at
`OpenCogCon <https://opencog.org/2020/07/virtual-opencogcon-july-15-16/>`__
and various
`AGI conferences <https://agi-conference.org/>`__.



How can it be used?
===================

To get a first impression of the package in action, here is a small code example.
More comprehensive
:doc:`examples <rst/examples/index>`
are available on separate pages.

.. code-block:: python

   import mevis as mv

   atomspace = mv.load('moses.scm')
   mv.plot(atomspace, 'vis', 'dot').export_html('moses_vis.html')
   mv.plot(atomspace, 'three', 'neato').export_html('moses_three.html')
   mv.plot(atomspace, 'd3', 'bipartite', edge_curvature=0.4).export_html('moses_d3.html')

   atomspace = mv.load('rocca.scm')
   atoms = mv.filter(atomspace, target=['SLink', 'MemberLink'], mode='exclude')
   graph = mv.convert(atoms, node_size=lambda atom: 30 if atom.type_name == 'SchemaNode' else 8)
   graph = mv.layout(graph, 'twopi', scale_x=2.0, scale_y=2.0)
   fig = mv.plot(graph, 'vis')
   fig.export_html('rocca_vis.html')


**Results**: This script generates the files
`moses_vis.html <_static/media/moses_vis.html>`__,
`moses_three.html <_static/media/moses_three.html>`__,
`moses_d3.html <_static/media/moses_d3.html>`__ and
`rocca_vis.html <_static/media/rocca_vis.html>`__.
These are self-contained HTML files, which means that they render without
loading any external resources and can be shared easily.
The package also allows to embed visualizations directly into
`Jupyter notebooks <https://jupyter.org>`__
or open them in a webbrowser window instead of creating standalone HTML files.

**Interpretation**: An AtomSpace consists of Atoms, which can be divided
into Nodes and Links. They are represented in this graph visualization by
red and black nodes, respectively.
Link-to-Node connections are represented by red edges and Link-to-Link
connections by black edges. Hovering over a node shows its
`Atomese <https://wiki.opencog.org/w/Atomese>`__
code.



Why is it relevant?
===================

During the development of OpenCog different
`requirements for AtomSpace visualizations <https://wiki.opencog.org/w/Atomspace_Visualization>`__
have appeared and at least
`eight visualization attempts <https://groups.google.com/g/opencog/c/pistqEX-5HI>`__
were created to meet some of them, but most have become obsolete by now.
This package is yet another attempt to fulfill some requirements and be of help
in certain situations described below. Its tight integration with Jupyter notebooks
is perhaps its most distinguishing feature in comparison to other approaches.



When should it be used?
=======================

- **Small graphs in Jupyter notebooks**:
  mevis is most useful for quick and interactive
  explorations of AtomSpaces below 1000 Atoms in Jupyter notebooks.
  Larger AtomSpaces can also be explored with some patience during rendering,
  but better by filtering them first so that the number of remaining Atoms
  is in a lower range.
  Notebooks can be exported as HTML files and shared with others,
  because the visualizations do not depend on external resources such
  as local files.
- **Small graphs in HTML files or as HTML text**:
  mevis can export plots as HTML files, which can also be shared with others,
  e.g. by embedding them into static websites such as this documentation.
  Another option is to read the HTML text of a plot and serve it
  as response to HTTP requests in a web app (e.g. with
  `Flask <https://flask.palletsprojects.com>`__
  or
  `Django <https://www.djangoproject.com/>`__).
- **Large graphs in external programs**:
  mevis can convert AtomSpaces to annotated
  `NetworkX <https://networkx.org/>`__
  graphs and export them
  in
  `GML format <https://en.wikipedia.org/wiki/Graph_Modelling_Language>`__
  or better in its compressed variants. This also works well with large AtomSpaces.
  The resulting ``.gml``, ``.gml.gz`` or ``.gml.bz2`` files can be read
  directly by external programs such as
  `Cytoscape <https://cytoscape.org/>`__,
  `Gephi <https://gephi.org/>`__
  or
  `Tulip <https://tulip.labri.fr/site/>`__,
  which are able to visualize very large graphs, though layout calculation
  may take quite a while.
- **Command line interface**:
  After installing this Python package with pip, the command ``mevis`` should be
  available in the shell, which offers `usage via CLI <code/examples/cli.ipynb>`__.
  It allows to load an AtomSpace from a ``.scm`` file, optionally filter it,
  convert it to a graph, optionally calculate a layout, and finally export
  the annotated graph to a GML file or create a plot of it, which can be
  displayed in a browser or exported to a HTML file. Thus the CLI allows
  to use most features of the package without having to write any Python code.



Who can benefit from it?
========================

- **OpenCog developers:**
  Quick visual feedback can help when new data sources are integrated into a single
  AtomSpace or when algorithms operating on AtomSpaces are developed and tested.
- **OpenCog users:**
  Simple visualization of AtomSpaces can help new arrivals but also experienced users
  by providing broad overviews or filtered perspectives of what is going on in a metagraph.
- **General audience:**
  OpenCog concepts such as knowledge representation with metagraphs,
  expression of both data and programs in Atomese,
  cognitive synergy of algorithms that can act on the same data,
  and similar ideas can be explained more vividly with accompanying visualizations
  and thereby might become more palpable to a diverse audience.



How can you get started?
========================

- The :doc:`installation guide <rst/installation>`
  explains how to download and install the package and its dependencies.
- The :doc:`examples <rst/examples/index>`
  provide an easy way to get started with using the package.
- The :doc:`API documentation <rst/api/index>` is the single source of truth
  for all details about each available function.



Where is everything located?
============================

The :doc:`package reference page <rst/package_references>`
contains links to all parts of this project, including
source code (with tests, docs, examples),
packaged code (for distribution via PyPI and pip)
and this documentation website.



Table of website contents
=========================

.. toctree::
   :maxdepth: 1

   rst/package_references
   rst/installation
   rst/examples/index
   rst/api/index
