# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from itertools import chain
from operator import itemgetter

from .axis import Attribute, Axis
from .predicate import Predicate


class Docpath:

    def __init__(self, steps):
        self.steps = steps

    def __truediv__(self, other):
        Predicate = self._get_predicate_class()
        if not isinstance(other, (Docpath, Predicate)):
            raise ValueError

        self_steps = self.steps
        if not isinstance(self_steps, list):
            self_steps = [self_steps]

        other_steps = other if isinstance(other, Predicate) else other.steps
        if not isinstance(other_steps, list):
            other_steps = [other_steps]

        return Docpath(self_steps + other_steps)

    def __floordiv__(self, other):
        descendant_or_self = Axis('descendant_or_self').node
        return self / descendant_or_self / other

    def __or__(self, other):
        if not isinstance(other, Docpath):
            raise ValueError

        self_steps = self.steps
        if not isinstance(self_steps, tuple):
            self_steps = (self_steps,)

        other_steps = other.steps
        if not isinstance(other_steps, tuple):
            other_steps = (other_steps,)

        return Docpath(self_steps + other_steps)

    def __getitem__(self, name):
        Predicate = self._get_predicate_class()
        return self / Predicate(name)

    def __repr__(self):
        return 'Docpath(\'{}\')'.format(self)

    def __str__(self):
        return self._str(self.steps)

    def _str(self, step):
        Predicate = self._get_predicate_class()
        if isinstance(step, DocpathStep):
            result = str(step)
        elif isinstance(step, Predicate):
            result = '[{}]'.format(step)
        elif isinstance(step, tuple):
            result = '(' + '|'.join([self._str(s) for s in step]) + ')'
        elif isinstance(step, list):
            result = '/'.join([self._str(s) for s in step])
            result = result.replace('/[', '[')
            if result.startswith('root::node'):
                result = result[len('root::node'):]
        else:
            raise ValueError
        return result

    def _get_predicate_class(self):
        return Predicate

    def find(self, from_node):
        return next(self.findall(from_node), None)

    def findall(self, from_node):
        node_addresses = list(self.traverse(from_node))
        node_addresses = sorted(node_addresses, key=itemgetter(1))
        return map(itemgetter(0), node_addresses)

    def traverse(self, from_node):
        from_address = Axis.node_address(from_node)
        yield from self._traverse(
            self.steps, None, [(from_node, from_address)])

    def _traverse(self, steps, predicates, node_addresses):
        result = None
        if isinstance(steps, DocpathStep):
            result = self._traverse_docpath(steps, predicates, node_addresses)
        elif isinstance(steps, tuple):
            result = self._traverse_tuple(steps, predicates, node_addresses)
        elif isinstance(steps, list):
            result = self._traverse_list(steps, predicates, node_addresses)
        else:
            raise ValueError("invalid path step: {}".format(steps))
        yield from result

    def _traverse_docpath(self, step, predicates, node_addresses):
        Predicate = self._get_predicate_class()

        result = []
        for node, address in node_addresses:
            result.append(
                Predicate.filter_nodes(
                    predicates,
                    step.filter_nodes(
                        step.axis.traverse(node, address))))

        return chain(*result)

    def _traverse_tuple(self, steps, predicates, node_addresses):
        Predicate = self._get_predicate_class()

        result = []
        for step in steps:
            result.append(self._traverse(step, None, node_addresses))

        return Predicate.filter_nodes(predicates, chain(*result))

    def _traverse_list(self, steps, predicates, node_addresses):
        Predicate = self._get_predicate_class()

        steps_with_predicates = []
        for step in steps:
            if isinstance(step, Predicate):
                predicate = step
                steps_with_predicates[-1][1].append(predicate)
            else:
                steps_with_predicates.append((step, []))

        for step_predicates in steps_with_predicates:
            node_addresses = self._traverse(*step_predicates, node_addresses)

        return Predicate.filter_nodes(predicates, node_addresses)


class DocpathStep:

    def __init__(self, axis, node_test):
        self.axis = axis
        self.node_test = node_test

    def __repr__(self):
        return 'DocpathStep(\'{}\')'.format(self)

    def __str__(self):
        return '{}::{}'.format(self.axis, self.node_test)

    def filter_nodes(self, node_addresses):
        return filter(self.perform_node_test, node_addresses)

    def perform_node_test(self, node_address):
        node, _ = node_address
        if isinstance(node, Attribute.Node):
            return self.node_test == node.name
        if self.node_test == 'node':
            return True
        if self.node_test == 'element':
            return node.__class__.__name__ not in ['Text', 'comment']
        if self.node_test == 'text':
            return node.__class__.__name__ == 'Text'
        return self.node_test == node.__class__.__name__
