# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from docpath import path
from unittest import TestCase


class TestDocpathParser(TestCase):

    def test_parser_relative(self):
        "Test docpath creation from a relative path."
        docpath = path('section')
        self.assertEqual(str(docpath), 'child::section')

    def test_parser_absolute(self):
        "Test docpath creation from an absolute path."
        docpath = path('/section')
        self.assertEqual(str(docpath), '/child::section')

    def test_parser_self(self):
        "Test docpath creation from a self path."
        docpath = path('./section')
        self.assertEqual(str(docpath), 'self::node/child::section')

    def test_parser_parent(self):
        "Test docpath creation from a parent path."
        docpath = path('../section')
        self.assertEqual(str(docpath), 'parent::node/child::section')

    def test_parser_wildcard(self):
        "Test docpath creation from a wildcard path."
        docpath = path('*')
        self.assertEqual(str(docpath), 'child::element')

    def test_parser_axis(self):
        "Test docpath creation from a wildcard path."
        docpath = path('following_sibling::section')
        self.assertEqual(str(docpath), 'following_sibling::section')

    def test_parser_complex(self):
        "Test docpath creation from a complex path."
        docpath = path('//section/.././following_sibling::*')
        self.assertEqual(
            str(docpath),
            '/descendant_or_self::node/child::section/parent::node'
            '/self::node/following_sibling::element')

    def test_parser_single_predicate(self):
        "Test docpath creation from a path containing a single predicate."
        docpath = path('section[1]')
        self.assertEqual(str(docpath), 'child::section[1]')

    def test_parser_multiple_predicates(self):
        "Test docpath creation from a path containing multiple predicates."
        docpath = path('section[@name == "n"][1]')
        self.assertEqual(
            str(docpath),
            'child::section[attribute.name == "n"][1]')

    def test_parser_or(self):
        "Test docpath creation from a path containing a single predicate."
        docpath = path('section|paragraph|title')
        self.assertEqual(
            str(docpath),
            '(child::section|child::paragraph|child::title)')

    def test_parser_or_middle(self):
        "Test docpath creation from a path containing a single predicate."
        docpath = path('node/(section|paragraph)/node')
        self.assertEqual(
            str(docpath),
            'child::node/(child::section|child::paragraph)/child::node')
