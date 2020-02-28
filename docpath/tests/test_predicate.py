# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from docpath.axis import Axis
from docpath.docpath import Docpath, DocpathStep
from docpath.predicate import Predicate
from docutils import nodes
from docutils.core import publish_doctree
from os.path import dirname, join
from unittest import TestCase


class TestPredicate(TestCase):

    def setUp(self):
        source = join(dirname(__file__), 'doc', 'doctree.rst')
        with open(source, 'r', encoding='utf-8') as rst:
            self.doctree = publish_doctree(rst.read())
        self.node = self.doctree.next_node(self._matches_node_i)

    @staticmethod
    def _matches_node_i(node):
        return not isinstance(node, nodes.Text) and node['names'] == ['i']

    def assertPredicate(self, axis, predicates, matches):
        path = Docpath([DocpathStep(axis, 'section')] + predicates)
        names = [', '.join(n['names']) for n, a in path.traverse(self.node)]
        self.assertEqual(names, matches)

    def assertPredicateRaises(self, axis, predicates, exception):
        path = Docpath([DocpathStep(axis, 'section')] + predicates)
        with self.assertRaises(exception):
            list(path.traverse(self.node))

    def test_predicate_true(self):
        "Test a predicate that is always true."
        self.assertPredicate(
            Axis('child'), [Predicate('True')],
            ['j', 'k', 'n', 'o', 'p'])

    def test_predicate_false(self):
        "Test a predicate that is always false."
        self.assertPredicate(
            Axis('child'), [Predicate('False')],
            [])

    def test_predicate_equality(self):
        "Test a predicate that contains an equality expression."
        self.assertPredicate(
            Axis('child'), [Predicate('position() == 2')],
            ['k'])

    def test_predicate_relational(self):
        "Test a predicate that contains a relational expression."
        self.assertPredicate(
            Axis('child'), [Predicate('position() > 2')],
            ['n', 'o', 'p'])

    def test_predicate_number(self):
        "Test a predicate that only contains a number."
        self.assertPredicate(
            Axis('child'), [Predicate('1')],
            ['j'])

    def test_predicate_number_expression(self):
        "Test a predicate that evaluates to a number."
        self.assertPredicate(
            Axis('child'), [Predicate('last()')],
            ['p'])

    def test_predicate_attribute_exists(self):
        "Test a predicate that tests whether an attribute exists."
        self.assertPredicate(
            Axis('child'), [Predicate('@names')],
            ['j', 'k', 'n', 'o', 'p'])

    def test_predicate_attribute_value(self):
        "Test a predicate that tests an attribute's value."
        self.assertPredicate(
            Axis('child'), [Predicate('@names == "n"')],
            ['n'])

    def test_predicate_node_exists(self):
        "Test a predicate that tests whether a node exists."
        self.assertPredicate(
            Axis('child'), [Predicate('./section')],
            ['k', 'p'])

    def test_predicate_node_value(self):
        "Test a predicate that tests a node's value."
        self.assertPredicate(
            Axis('child'), [Predicate('./section == "Q"')],
            ['p'])

    def test_predicate_count_nodeset(self):
        "Test a predicate that counts the amount of nodes in a path."
        self.assertPredicate(
            Axis('child'), [Predicate('count(^//section) == 21')],
            ['j', 'k', 'n', 'o', 'p'])

    def test_predicate_forward_axis(self):
        "Test a predicate that uses a forward axis."
        self.assertPredicate(
            Axis('following_sibling'), [Predicate('1')],
            ['s'])

    def test_predicate_reverse_axis(self):
        "Test a predicate that uses a reverse axis."
        self.assertPredicate(
            Axis('preceding_sibling'), [Predicate('1')],
            ['h'])

    def test_predicate_double_number(self):
        "Test multiple predicates that select nodes by number."
        self.assertPredicate(
            Axis('child'), [Predicate('4'), Predicate('1')],
            ['o'])

    def test_predicate_double_number_all_filtered_out(self):
        "Test multiple predicates that select no nodes."
        self.assertPredicate(
            Axis('child'), [Predicate('1'), Predicate('4')],
            [])

    def test_predicate_not_element(self):
        "Test a predicate that find nodes that do not match."
        path = Docpath([
            DocpathStep(Axis('descendant_or_self'), 'node'),
            Predicate('name() != "section"')])
        self.assertEqual(
            [n[0].__class__.__name__ for n in path.traverse(self.node)],
            ['title', 'Text', 'title', 'Text', 'title', 'Text', 'title',
             'Text', 'title', 'Text', 'title', 'Text', 'title', 'Text',
             'title', 'Text', 'title', 'Text', 'title', 'Text'])

    def test_predicate_associates_with_last_step(self):
        "Test a predicate that finds the first child section of all nodes."
        path = Docpath([
            DocpathStep(Axis('root'), 'node'),
            DocpathStep(Axis('descendant_or_self'), 'node'),
            DocpathStep(Axis('child'), 'section'),
            Predicate('1')])
        self.assertEqual(
            [' '.join(n['names']) for n, _ in path.traverse(self.node)],
            ['c', 'f', 'g', 'j', 'l', 'q', 'u'])

    def test_predicate_assignment_operator(self):
        "Test a predicate cannot contain an assignment operator."
        self.assertPredicateRaises(
            Axis('child'), [Predicate('./section = "Q"')],
            SyntaxError)
        self.assertPredicateRaises(
            Axis('child'), [Predicate('@attribute = "Q"')],
            SyntaxError)
