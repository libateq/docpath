# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
import ast
import operator

from simpleeval import safe_add, safe_mult, simple_eval

from .axis import Axis


class Predicate:

    def __init__(self, predicate):
        self._raw_predicate = predicate

    def __repr__(self):
        return 'Predicate(\'{}\')'.format(self)

    def __str__(self):
        return self.predicate

    @property
    def predicate(self):
        if not getattr(self, '_predicate', None):
            predicate = self._raw_predicate
            replacements = {
                '::': '.',
                '../': 'parent.node/',
                './': 'self.node/',
                '^/': 'root.node/',
                '@': 'attribute.',
                '.*': '.element',
            }
            for replacement in replacements.items():
                predicate = predicate.replace(*replacement)
            self._predicate = predicate

        return self._predicate

    @classmethod
    def filter_nodes(cls, predicates, node_addresses):
        if predicates:
            for predicate in predicates:
                node_addresses = predicate._filter_nodes(node_addresses)
        return node_addresses

    def _filter_nodes(self, node_addresses):
        node_addresses = list(node_addresses)
        result = []
        position = 1
        for node, address in node_addresses:
            context = {
                'address': address,
                'node': node,
                'size': len(node_addresses),
                'position': position,
            }
            if self.perform_predicate_test(**context):
                result.append((node, address))
            position += 1
        return result

    def perform_predicate_test(self, **context):
        from .docpath import Docpath

        predicate_type = type(ast.parse(self.predicate).body[0])
        if predicate_type == ast.Assign:
            raise SyntaxError(
                "invalid use of assignment operator in: '{}'".format(
                    self.predicate))

        result = simple_eval(
            self.predicate, **self._get_evaluation_context(**context))

        if isinstance(result, Docpath):
            nodes = result.traverse(context['node'])
            matches = len(list(nodes))
            return matches > 0
        elif str(result).isdigit():
            return result == context.get('position', None)

        return bool(result)

    @staticmethod
    def _get_evaluation_context(**context):
        node = context.get('node', None)
        position = context.get('position', None)
        size = context.get('size', None)

        def name_handler(name):
            try:
                return Axis(name.id)
            except ValueError:
                return getattr(Axis('child'), name.id)

        return {
            'functions': {
                'count': lambda x: count(node, x),
                'last': lambda: size,
                'name': lambda *x: name(node, *x),
                'position': lambda: position,
            },
            'names': name_handler,
            'operators': {
                ast.Eq: lambda l, r: compare(node, l, r, operator.eq),
                ast.NotEq: lambda l, r: compare(node, l, r, operator.ne),
                ast.Lt: lambda l, r: compare(node, l, r, operator.lt),
                ast.LtE: lambda l, r: compare(node, l, r, operator.le),
                ast.Gt: lambda l, r: compare(node, l, r, operator.gt),
                ast.GtE: lambda l, r: compare(node, l, r, operator.ge),
                ast.Add: safe_add,
                ast.Sub: operator.sub,
                ast.Mult: safe_mult,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.And: operator.and_,
                ast.Or: operator.or_,
                ast.Not: operator.not_,
                ast.UAdd: operator.pos,
                ast.USub: operator.neg,
            },
        }


def compare(node, left, right, op):
    from .docpath import Docpath

    if isinstance(left, Docpath):
        left = set([n.astext() for n in left.findall(node)])
    if isinstance(right, Docpath):
        right = set([n.astext() for n in right.findall(node)])

    if isinstance(left, set) or isinstance(right, set):
        left = left if isinstance(left, set) else set((left,))
        right = right if isinstance(right, set) else set((right,))

        if op in (operator.eq, operator.ne):
            return op(bool(left & right), True)
        if op in (operator.lt, operator.le):
            return op(min(left), max(right))
        if op in (operator.gt, operator.ge):
            return op(max(left), min(right))

    return op(left, right)


def count(node, value):
    from .docpath import Docpath

    if isinstance(value, Docpath):
        return len(list(value.findall(node)))
    return len(value)


def name(node, value=None):
    from .docpath import Docpath

    target = None
    if value is None:
        target = node
    elif isinstance(value, Docpath):
        target = value.find(node)

    return target.__class__.__name__
