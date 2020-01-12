Usage
=====

The purpose of the *docpath* package is to add support for `xpath 1.0`_ style
paths to docutils_ doctrees.  The syntax used to specify docpaths can be found
on the :doc:`docpath` page.

.. _docutils: http://docutils.sourceforge.net/
.. _`xpath 1.0`: https://www.w3.org/TR/xpath-10/


Creating Docpaths
-----------------

Once the package is installed, docpaths can be created using the path function.

.. py:function:: path(docpath)

    :param str docpath: The value to parse into a docpath.
    :return: the :py:class:`Docpath` that the parameter represented.

    Parses the ``docpath`` and creates a :py:class:`Docpath` instance.  This
    :py:class:`Docpath` instance can be used to query a docutils doctree for
    nodes that match the path.

    Example:

    .. code-block:: python3

        from docpath import path

        docpath = path('//section/title')

Using Docpaths
--------------

Now that you have a :py:class:`Docpath`, you can use some of its methods to
iterate though, or get, matching nodes from a doctree.

Some of these functions produce nodes in what is called *document order*.  This
is the order that you would encounter the nodes if you were to read the
document from start to finish.

The examples in this section assume you have created a docpath as shown in the
:py:func:`path` function and loaded a document into a docutils doctree:

.. code-block:: python3

    from docutils.core import publish_doctree

    with open('doctree.rst', 'r', encoding='utf-8') as rst:
        doctree = publish_doctree(rst.read())


.. py:class:: Docpath

    .. py:function:: find(from_node)

        :param node from_node: The context node that relative docpaths start
                               from.
        :return: The first node, in document order, that matches the node.

        Finds and returns the first node, in document order, that matches the
        docpath.  If the docpath is a relative path, then the returned node is
        relative to the ``from_node``.  If the docpath is absolute then the
        nodes are from the same document as the ``from_node``.

        For example, to find the first section title node in a document:

        .. code-block:: python3

            title_node = docpath.find(doctree)


    .. py:function:: findall(from_node)

        :param node from_node: The context node that relative docpaths start
                               from.
        :return: an iterator that iterates over the matching nodes in document
                 order.

        Iterates, in document order, over the nodes that match the docpath.
        If the docpath is a relative path, then the returned nodes are relative
        to the ``from_node``.  If the docpath is absolute then the nodes are
        from the same document as the ``from_node``.

        For example, to find all the section title nodes in a document in
        document order:

        .. code-block:: python3

            title_nodes = list(docpath.findall(doctree))


    .. py:function:: traverse(from_node)

        :param node from_node: The context node that relative docpaths start
                               from.
        :return: an iterator that iterates over the matching nodes and returns
                 (node, address) tuples for each of them.

        Iterates over the node and address pairs that match the docpath. If the
        docpath is a relative path, then the nodes that are returned are
        relative to the ``from_node``.  If the docpath is absolute then the
        nodes are from the same document as the ``from_node``.

        The addresses of the nodes are tuples containing a list of child
        indexes to follow from the root node down to the node.

        The order that the nodes are iterated over is dependant on the axes in
        the path, and this is not generally in document order.

        For example, to print the address and name of each section title in a
        document (where the order doesn't matter):

        .. code-block:: python3

            for node, address in docpath.traverse(doctree):
                print(address, node.astext())
