# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from docpath import path
from docpath.axis import Axis
from docpath.docpath import Docpath, DocpathStep
from docutils import nodes
from docutils.core import publish_doctree
from os.path import dirname, join
from unittest import TestCase


class TestDocpath(TestCase):

    def setUp(self):
        source = join(dirname(__file__), 'doc', 'doctree.rst')
        with open(source, 'r', encoding='utf-8') as rst:
            self.doctree = publish_doctree(rst.read())
        self.node = self.doctree.next_node(self._matches_node_i)

    @staticmethod
    def _matches_node_i(node):
        return not isinstance(node, nodes.Text) and node['names'] == ['i']

    def test_docpath_creation(self):
        "Test docpath creation."
        path = Docpath(DocpathStep(Axis('child'), 'section'))
        self.assertEqual(str(path), 'child::section')

    def test_docpath_creation_steps(self):
        "Test docpath creation from steps."
        path = Docpath([
            DocpathStep(Axis('root'), 'node'),
            DocpathStep(Axis('child'), 'section')])
        self.assertEqual(str(path), '/child::section')

    def test_docpath_creation_step_or(self):
        "Test docpath creation from or steps."
        path = Docpath((
            DocpathStep(Axis('root'), 'node'),
            DocpathStep(Axis('child'), 'section')))
        self.assertEqual(str(path), '(root::node|child::section)')

    def test_docpath_traverse(self):
        "Test docpath traverse."
        docpath = path('//section')
        self.assertEqual(
            [', '.join(n['names']) for n, a in docpath.traverse(self.node)],
            ['c', 'd', 'e', 'v', 'w', 'f', 'h', 'i', 's', 't', 'g', 'j', 'k',
             'n', 'o', 'p', 'l', 'm', 'q', 'r', 'u'])

    def test_docpath_findall(self):
        "Test docpath findall."
        docpath = path('//section')
        self.assertEqual(
            [', '.join(n['names']) for n in docpath.findall(self.node)],
            ['c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
             'p', 'q', 'r', 's', 't', 'u', 'v', 'w'])

    def test_docpath_find(self):
        "Test docpath find."
        docpath = path('//section')
        self.assertEqual(
            docpath.find(self.node)['names'],
            ['c'])

    def test_docpath_find_nothing(self):
        "Test docpath find that returns None."
        docpath = path('paragraph')
        self.assertIsNone(docpath.find(self.node))

    def test_docpath_or(self):
        "Test docpaths or."
        docpath = path('/self::document|//subtitle|//section')
        self.assertEqual(
            [', '.join(n['names']) for n in docpath.findall(self.node)],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
             'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w'])


class TestDocpathStep(TestCase):

    def setUp(self):
        source = join(dirname(__file__), 'doc', 'doctree.rst')
        with open(source, 'r', encoding='utf-8') as rst:
            self.doctree = publish_doctree(rst.read())
        self.node = self.doctree.next_node(self._matches_node_i)
        self.node_addresses = [
            (nodes.section(), ()),
            (nodes.paragraph(), ()),
            (nodes.comment(), ()),
            (nodes.Text('text'), ())]

    @staticmethod
    def _matches_node_i(node):
        return not isinstance(node, nodes.Text) and node['names'] == ['i']

    def assertFilterNodes(self, node_test, matches):
        step = DocpathStep(Axis('child'), node_test)
        filtered_nodes = step.filter_nodes(self.node_addresses)
        self.assertEqual(list(filtered_nodes), matches)

    def test_docpathstep_filter_nodes_node(self):
        "Test docpath step filter nodes for nodes."
        self.assertFilterNodes('node', self.node_addresses)

    def test_docpathstep_filter_nodes_element(self):
        "Test docpath step filter nodes for elements."
        self.assertFilterNodes('element', self.node_addresses[:2])

    def test_docpathstep_filter_nodes_comment(self):
        "Test docpath step filter nodes for comments."
        self.assertFilterNodes('comment', self.node_addresses[2:3])

    def test_docpathstep_filter_nodes_text(self):
        "Test docpath step filter nodes for text."
        self.assertFilterNodes('text', self.node_addresses[3:4])

    def test_docpathstep_filter_nodes_section(self):
        "Test docpath step filter nodes for section."
        self.assertFilterNodes('section', self.node_addresses[0:1])
