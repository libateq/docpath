# This file is part of the docpath package.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.


class Axis:

    def __new__(cls, name):
        axes = cls.axes()
        if name not in axes:
            raise ValueError
        return super().__new__(axes[name])

    def __getattr__(self, name):
        from .docpath import Docpath, DocpathStep
        return Docpath(DocpathStep(self, name))

    def __repr__(self):
        return 'Axis(\'{}\')'.format(self)

    def __str__(self):
        return self._name

    @classmethod
    def axes(cls):
        return {a._name: a for a in Axis.__subclasses__()}

    @classmethod
    def node_address(cls, node):
        address = []
        for ancestor, _ in AncestorOrSelf.traverse_backwards(node, ()):
            if not ancestor.parent:
                address.append(1)
            else:
                address.append(ancestor.parent.index(ancestor))
        return tuple(address)

    @classmethod
    def traverse(cls, node, address):
        raise NotImplementedError

    @classmethod
    def traverse_backwards(cls, node, address):
        for node, address in reversed(list(cls.traverse(node, address))):
            yield node, address


class Ancestor(Axis):
    _name = 'ancestor'
    _reverse = True

    @classmethod
    def traverse(cls, node, address):
        while node.parent:
            node = node.parent
            address = address[:-1]
            yield node, address

    @classmethod
    def traverse_backwards(cls, node, address):
        yield from reversed(list(cls.traverse(node, address)))


class AncestorOrSelf(Axis):
    _name = 'ancestor_or_self'
    _reverse = True

    @classmethod
    def traverse(cls, node, address):
        yield node, address
        yield from Ancestor.traverse(node, address)

    @classmethod
    def traverse_backwards(cls, node, address):
        yield from Ancestor.traverse_backwards(node, address)
        yield node, address


class Attribute(Axis):
    _name = 'attribute'

    class Node:
        def __init__(self, name, value):
            self.name = name
            self.value = value

        def astext(self):
            if isinstance(self.value, (list, tuple)):
                return ' '.join(self.value)
            else:
                return str(self.value)

    @classmethod
    def traverse(cls, node, address):
        for i, (name, value) in enumerate(node.attributes.items()):
            yield cls.Node(name, value), address + (i,)


class Child(Axis):
    _name = 'child'

    @classmethod
    def traverse(cls, node, address):
        for i, child in enumerate(node.children):
            yield child, address + (i,)

    @classmethod
    def traverse_backwards(cls, node, address):
        for i, child in reversed(list(enumerate(node.children))):
            yield child, address + (i,)


class Descendant(Axis):
    _name = 'descendant'

    @classmethod
    def traverse(cls, node, address):
        for child_address in Child.traverse(node, address):
            yield child_address
            yield from cls.traverse(*child_address)

    @classmethod
    def traverse_backwards(cls, node, address):
        for child_address in Child.traverse_backwards(node, address):
            yield from cls.traverse_backwards(*child_address)
            yield child_address


class DescendantOrSelf(Axis):
    _name = 'descendant_or_self'

    @classmethod
    def traverse(cls, node, address):
        yield node, address
        yield from Descendant.traverse(node, address)

    @classmethod
    def traverse_backwards(cls, node, address):
        yield from Descendant.traverse_backwards(node, address)
        yield node, address


class Following(Axis):
    _name = 'following'

    @classmethod
    def traverse(cls, node, address):
        for ancestor in AncestorOrSelf.traverse(node, address):
            for sibling in FollowingSibling.traverse(*ancestor):
                yield sibling
                yield from Descendant.traverse(*sibling)


class FollowingSibling(Axis):
    _name = 'following_sibling'

    @classmethod
    def traverse(cls, node, address):
        if node.parent:
            index = node.parent.index(node)
            siblings = node.parent.children[index+1:]
            for i, sibling in enumerate(siblings):
                yield sibling, address[:-1] + (index + i + 1,)


class Parent(Axis):
    _name = 'parent'
    _reverse = True

    @classmethod
    def traverse(cls, node, address):
        if node.parent:
            yield node.parent, address[:-1]

    @classmethod
    def traverse_backwards(cls, node, address):
        yield from cls.traverse(node, address)


class Preceding(Axis):
    _name = 'preceding'
    _reverse = True

    @classmethod
    def traverse(cls, node, address):
        for ancestor in AncestorOrSelf.traverse(node, address):
            for sibling in PrecedingSibling.traverse(*ancestor):
                yield from DescendantOrSelf.traverse_backwards(*sibling)

    @classmethod
    def traverse_backwards(cls, node, address):
        for ancestor in AncestorOrSelf.traverse_backwards(node, address):
            for sibling in PrecedingSibling.traverse_backwards(*ancestor):
                yield from DescendantOrSelf.traverse(*sibling)


class PrecedingSibling(Axis):
    _name = 'preceding_sibling'
    _reverse = True

    @classmethod
    def traverse(cls, node, address):
        if node.parent:
            index = node.parent.index(node)
            siblings = node.parent.children[:index]
            for i, sibling in reversed(list(enumerate(siblings))):
                yield sibling, address[:-1] + (i,)

    @classmethod
    def traverse_backwards(cls, node, address):
        if node.parent:
            index = node.parent.index(node)
            siblings = node.parent.children[:index]
            for i, sibling in enumerate(siblings):
                yield sibling, address[:-1] + (i,)


class Root(Axis):
    _name = 'root'

    @classmethod
    def traverse(cls, node, address):
        yield node.document, (1,)


class Self(Axis):
    _name = 'self'

    @classmethod
    def traverse(cls, node, address):
        yield node, address
