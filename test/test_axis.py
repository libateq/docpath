# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from docpath.axis import Axis
from docutils import nodes
from docutils.core import publish_doctree
from os.path import dirname, join
from unittest import TestCase


class TestAxis(TestCase):

    def setUp(self):
        source = join(dirname(__file__), 'doc', 'doctree.rst')
        with open(source, 'r', encoding='utf-8') as rst:
            self.doctree = publish_doctree(rst.read())
        self.node = self.doctree.next_node(self._matches_node_i)
        self.address = Axis.node_address(self.node)

    @staticmethod
    def _matches_node_i(node):
        return not isinstance(node, nodes.Text) and node['names'] == ['i']

    def assertAttributeTraversal(self, traverse, matches):
        attributes = set([
            n.name for n, _ in traverse(self.node, self.address)])
        self.assertEqual(attributes, matches)

    def assertNameTraversal(self, traverse, matches):
        names = [
            ', '.join(n['names'])
            for n, _ in traverse(self.node, self.address)
            if not isinstance(n, nodes.Text) and n['names']]
        self.assertEqual(names, matches)

    def test_axis_node_address(self):
        "Test the node address is calculated correctly."
        self.assertEqual(Axis.node_address(self.node), (1, 4, 3))

    def test_axis_traverse_ancestor(self):
        "Test the ancestor doctree traversal."
        self.assertNameTraversal(
            Axis('ancestor').traverse,
            ['e', 'a'])
        self.assertNameTraversal(
            Axis('ancestor').traverse_backwards,
            ['a', 'e'])

    def test_axis_traverse_ancestor_or_self(self):
        "Test the ancestor or self doctree traversal."
        self.assertNameTraversal(
            Axis('ancestor_or_self').traverse,
            ['i', 'e', 'a'])
        self.assertNameTraversal(
            Axis('ancestor_or_self').traverse_backwards,
            ['a', 'e', 'i'])

    def test_axis_traverse_attribute(self):
        "Test the attribute doctree traversal."
        self.assertAttributeTraversal(
            Axis('attribute').traverse,
            set(['backrefs', 'names', 'classes', 'dupnames', 'ids']))

    def test_axis_traverse_child(self):
        "Test the child doctree traversal."
        self.assertNameTraversal(
            Axis('child').traverse,
            ['j', 'k', 'n', 'o', 'p'])
        self.assertNameTraversal(
            Axis('child').traverse_backwards,
            ['p', 'o', 'n', 'k', 'j'])

    def test_axis_traverse_descendant(self):
        "Test the descendant doctree traversal."
        self.assertNameTraversal(
            Axis('descendant').traverse,
            ['j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r'])
        self.assertNameTraversal(
            Axis('descendant').traverse_backwards,
            ['r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j'])

    def test_axis_traverse_descendant_or_self(self):
        "Test the descendant or self doctree traversal."
        self.assertNameTraversal(
            Axis('descendant_or_self').traverse,
            ['i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r'])
        self.assertNameTraversal(
            Axis('descendant_or_self').traverse_backwards,
            ['r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i'])

    def test_axis_traverse_following(self):
        "Test the following doctree traversal."
        self.assertNameTraversal(
            Axis('following').traverse,
            ['s', 't', 'u', 'v', 'w'])
        self.assertNameTraversal(
            Axis('following').traverse_backwards,
            ['w', 'v', 'u', 't', 's'])

    def test_axis_traverse_following_sibling(self):
        "Test the following sibling doctree traversal."
        self.assertNameTraversal(
            Axis('following_sibling').traverse,
            ['s', 't'])
        self.assertNameTraversal(
            Axis('following_sibling').traverse_backwards,
            ['t', 's'])

    def test_axis_traverse_parent(self):
        "Test the parent doctree traversal."
        self.assertNameTraversal(
            Axis('parent').traverse,
            ['e'])
        self.assertNameTraversal(
            Axis('parent').traverse_backwards,
            ['e'])

    def test_axis_traverse_preceding(self):
        "Test the preceding doctree traversal."
        self.assertNameTraversal(
            Axis('preceding').traverse,
            ['h', 'g', 'f', 'd', 'c', 'b'])
        self.assertNameTraversal(
            Axis('preceding').traverse_backwards,
            ['b', 'c', 'd', 'f', 'g', 'h'])

    def test_axis_traverse_preceding_sibling(self):
        "Test the preceding sibling doctree traversal."
        self.assertNameTraversal(
            Axis('preceding_sibling').traverse,
            ['h', 'f'])
        self.assertNameTraversal(
            Axis('preceding_sibling').traverse_backwards,
            ['f', 'h'])

    def test_axis_traverse_root(self):
        "Test the root doctree traversal."
        self.assertNameTraversal(
            Axis('root').traverse,
            ['a'])
        self.assertNameTraversal(
            Axis('root').traverse_backwards,
            ['a'])

    def test_axis_traverse_self(self):
        "Test the self doctree traversal."
        self.assertNameTraversal(
            Axis('self').traverse,
            ['i'])
        self.assertNameTraversal(
            Axis('self').traverse_backwards,
            ['i'])
