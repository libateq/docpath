# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
import ast
import operator

from collections import namedtuple
from re import compile
from simpleeval import simple_eval

from .axis import Axis
from .docpath import Docpath


def path(docpath):
    return DocpathParser.parse(docpath)


class DocpathParser:

    Token = namedtuple('Token', 'name value')

    _name_re = r'([a-zA-Z_][a-zA-Z0-9_.-]*)'

    literals = [
        '@', '::', '..', '.', '//', '/', '|', '*', '(', ')', '[']

    tokens = [
        ('space', r'(\s+)'),

        ('axis', r'({})(?=\s*::)'.format(_name_re)),
        ('function', r'({})(?=\s*\()'.format(_name_re)),
        ('name', _name_re),
    ] + [(l, '({})'.format(''.join(['\\' + c for c in l]))) for l in literals]

    predicate_tokens = [
        ('[', r'(\[)'),
        (']', r'(\])'),
        ('literal', r'(("[^"]*")|(\'[^\']*\'))'),
        ('predicate_contents', r'([^\[\]\"\']+)'),
    ]

    @classmethod
    def lexer(cls, docpath, start_pos=0, tokens=None):
        if tokens is None:
            tokens = cls.tokens
        if isinstance(tokens[0][1], str):
            tokens = [(k, compile(v)) for k, v in tokens]

        pos = start_pos
        while pos < len(docpath):
            match = None
            for token, pattern in tokens:
                match = pattern.match(docpath, pos)
                if match:
                    pos = match.end()
                    match = cls.Token(token, match.group(0))
                    break

            if not match:
                raise ValueError(
                    "syntax error in docpath '{}' at position {}".format(
                        docpath, pos))

            if match.name == '[':
                match = cls._lexer_predicate(docpath, pos)
                pos += len(match.value) - 1

            yield match

    @classmethod
    def _lexer_predicate(cls, docpath, start_pos=0):
        pos = start_pos
        predicate = ['[']
        for match in cls.lexer(docpath, pos, cls.predicate_tokens):
            predicate.append(match.value)
            pos += len(match.value)
            if match.name == ']':
                break

        if match.name != ']':
            raise ValueError(
                "unterminated predicate in docpath '{}' at position {}".format(
                    docpath, start_pos))

        return cls.Token('predicate', ''.join(predicate))

    @classmethod
    def parse(cls, docpath):
        replacements = {
            '::': '.',
            '..': 'parent.node',
            '.': 'self.node',
            '@': 'attribute.',
            '*': 'element',
        }

        expression = []
        last_token_name = None
        for token in cls.lexer(docpath):
            part = replacements.get(token.name, token.value)
            if token.name == 'predicate':
                part = '["{}"]'.format(part[1:-1].replace('"', r'\"'))

            if part.startswith('/') and last_token_name in [None, '|', '(']:
                part = 'root.node' + part

            expression.append(part)
            last_token_name = token.name

        expression = ''.join(expression)
        return cls.evaluate(expression)

    @classmethod
    def evaluate(cls, path):
        result = simple_eval(path, **cls._get_evaluate_context())

        if not isinstance(result, Docpath):
            raise ValueError("invalid path: {}".format(path))

        return result

    @classmethod
    def _get_evaluate_context(cls):
        def name_handler(name):
            try:
                return Axis(name.id)
            except ValueError:
                return getattr(Axis('child'), name.id)

        return {
            'functions': {},
            'names': name_handler,
            'operators': {
                ast.BitOr: operator.or_,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
            },
        }
