Docpaths
========

Docpaths are `xpath 1.0`_ style paths that can be used with docutils_ doctrees.
They should feel familiar to you if you have used xpaths before, but even
though they are similar there are a few differences to the syntax and available
functions.

.. _docutils: http://docutils.sourceforge.net/
.. _`xpath 1.0`: https://www.w3.org/TR/xpath-10/


Examples
--------

To quickly get an idea of the kind of docpaths that can be created, and to get
you started here are some example docpaths, along with a description of the
nodes that they select.  See the Syntax_ section below for a in-depth
reference.

``title``
    This selects all the title nodes that are children of the context node.

``paragraph[1]``
    This selects the first paragraph that is a child of the context node.

``paragraph[last()]``
    This selects the last paragraph that is a child of the context node.

``paragraph[position() <= 3]``
    This selects the first three paragraphs that are children of the context
    node.

``node[name() != "section"]``
    This selects the children of the context node that are not sections.

``preceding_sibling::paragraph[1]``
    This selects the previous paragraph sibling of the context node.

``following_sibling::paragraph[1]``
    This selects the next paragraph sibling of the context node.

``/section``
    This selects the top level sections in the document.

``/section[2]/paragraph[3]/bullet_list``
    This selects the bullet_list that appears in the third paragraph of the
    second top level section.

``/descendant_or_self::node/child::section``
    This selects all the sections in the document, regardless of level.

``//section``
    This selects all the sections in the document, regardless of level, and is
    abbreviated syntax for the previous example.

``//section[title=="Examples"]``
    This selects the section that has a child title node whose string value is
    equal to ``Examples``, or put more simply this selects the section called
    ``Examples``, regardless of what level it is at.

``//bullet_list/list_item``
    This selects the all the list_item nodes that are in bullet_lists.


Syntax
------

In general docpaths are comprised of one or more steps, separated by a forward
slash (``/``).  Each step can be made up from an axis, a node test and some
optional predicates.  If an axis is specified, then it must be immediately
followed by a double colon (``::``). If no axis is specified then it defaults
to the ``child`` axis, and the double colon should also be omitted.  Any
predicates must appear inside square brackets (``[``, and ``]``).
E.g. ``ancestor::section/child::title[1]``

Docpaths can be combined together using an ``|`` operator, this merges the
result of the two docpaths together.
E.g. ``(child::section|child::paragraph)[1]`` would find the first child node
that is either section or paragraph.

Docpaths steps are evaluated with respect to a context.  The context contains
a context node, a context position and context size.  If a docpaths starts with
a ``/`` then it is said to be an absolute path, and selects nodes that are
with respect to the root node of the document.  Other docpaths are relative
paths and select nodes with respect to the context node.


Axes
^^^^

An axis specifies the tree relationship between the context node and the nodes
that are selected by the axis.  For example, the ``child`` axis will select all
the children nodes of the context node.

The available axes are:

``ancestor``
    All direct ancestors of the node up to and including the root node.  In
    other words, the context node's parent, the parent's parent and so on
    all the way up to the root node.

``ancestor_or_self``
    All the nodes selected by the ``ancestor`` axis and also the context node.

``attribute``
    A special axis that selects the attributes of the context node.

``child``
    All the children nodes of the context node.

``descendant``
    All the children nodes of the context node, and their children nodes, and
    so on down to the bottom of the tree. 

``descendant_or_self``
    All the nodes selected by the ``descendant`` axis and also the context
    node.

``following``
    All nodes that occur in the document after the context node.

``following_sibling``
    All siblings nodes of the context node that occur after it.

``parent``
    The parent node of the context node.

``preceding``
    All nodes that occur in the document before the context node.

``preceding_sibling``
    All siblings nodes of the context node that occur before it.

``self``
    The context node.

As you can probably see, the names of the docpath axes are the same as xpath
axes, but with ``-`` characters converted to ``_`` characters instead.

The ``ancestor``, ``descendant``, ``following``, ``preceding`` and ``self``
axes partition a document.  They do not overlap, and together contain all of
the nodes from the document.

The ``ancestor``, ``ancestor_or_self``, ``parent``, ``preceding``, and
``preceding_sibling`` axes are reverse axes.  This means that their nodes are
traversed in reverse order.  This is important to know when using predicate
expressions that depend on the position of the node.


Node Test
^^^^^^^^^

A node test is either the name of a type of node, or one of the special node
types listed below.  The ``*`` character can also be used and is short for
``element``.  The node test is used to filter the nodes that are selected by
an axis.  If a node test is the name of a type of node then only nodes of that
type will be selected.

The special node types select the following types of node:

``node``
    All nodes match this node type, use this if you don't want to filter out
    any nodes.

``element``
    Selects all nodes that are not ``text``, or ``comment`` nodes.

``text``
    Only selects nodes that are docutils Text nodes.

``comment``
    Only selects nodes that are docutils comment nodes.

These special node types behave similarly to the *NodeType* functions in
xpath, except that they should not be followed by ``()``.

For example a node test of ``section`` will mean that only section nodes will
be selected by the associated docpath step.


Predicates
^^^^^^^^^^

Predicates are defined inside square brackets (``[``, and ``]``).  They filter
nodes-sets that are generated in docpath steps to produce new node-sets.  For
each node in the node-set the predicate expression is evaluated.  If the
predicate evaluates to true for the node then it is included in the new
node-set, otherwise it is not included.

A predicate is evaluated with respect to a context.  The context node is the
node from the preceding docpath step.  The context size is the number of nodes
in the node-set, and the context position is the position of the node in the
node-set.

Predicates can be chained together, the resulting node-set from one predicate
is passed through to the next predicate.  The context size and position are
recalculated for each predicate.

When a predicate is evaluated its result is converted to a boolean in
different ways depending on the type of the result:

* *integer*: the result is compared to the value of the :py:func:`position`
  function, if it matches then the result is converted to ``True``, otherwise
  it is converted to ``False``.
* *Docpath*: the docpath is evaluated to get a node-set.  If the node-set
  contains any nodes then the result is converted to ``True``, if the node-set
  is empty then it is converted to ``False``.
* everything else is converted to a boolean using the :py:func:`bool` function.

Docpaths can be included in predicates, and produce node-sets that can be
passed to functions or compared to other values or docpaths.

.. note:: One minor difference to normal docpaths is that absolute paths must
          be preceded  with the ^ character when they are inside a predicate
          (e.g. ``^//section``).

Predicates can contain the following operators:

* comparison: ``==``, ``!=``, ``<``, `<=```, ``>``, ``>=``
* arithmetic: ``+``, `-```, ``*``, ``/``, ``//``, ``mod``
* logical: ``and``, ``or``, ``not``
* unary: ``+``, ``-``

The comparison operators work as normal except when one, or both, of its
operands is a node-set.  In this case the nodes in the node-sets are first
converted to values using the nodes :py:func:`astext` function.  If both
operands are node-sets then the comparison is true if there exists any node in
the first node-set and any node in the second node-set such that when their
values are compared would make the result true.  If one of the operands is a
node-set then the result is true if the value of any node from the node-set
when compared to the other value would make the result true.

Predicates can contain the following functions:

.. py:function:: count(value)

    :param value: The value to be counted.
    :return: the length of the value.

    If the value is a docpath then the number of nodes in it's node-set is
    returned, otherwise the result is the :py:func:`len` of the value.


.. py:function:: last()

    :return: the index of the last item in the context node-set.

    The return value is the context size from the evaluation context.


.. py:function:: name([value])

    :param node-set value: An optional node-set.
    :return: the type of first node in document order from the node-set.

    The name of the type of the first node is calculated and returned.  The
    nodes in the node-set are ordered in document order.  If no node-set is
    provided then the name of the type of the context node is returned instead.


.. py:function:: position()

    :return: the position of the node in the node-set.

    The return value is the context position from the evaluation context.


Abbreviations
^^^^^^^^^^^^^

In order to make the docpaths shorter and more convenient there are some
abbreviations that can be used which mirror similar abbreviations from xpaths:

* ``child::`` can be omitted as it is the default axis. 
* ``//`` is short for ``/descendant_or_self::node/``
* ``..`` is short for ``parent::node``
* ``.`` is short for ``self::node``
* ``@`` is short for ``attribute::``
* ``*`` is short for ``element``
