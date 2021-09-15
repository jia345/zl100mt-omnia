# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2013 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from xml.etree import cElementTree as ET


anon_path = re.compile(r"@(?P<name>[\w\-]+)\[(?P<pos>\-?\d+)]")


class YinElement(object):
    tag = ""
    NS_URI = "urn:ietf:params:xml:ns:netconf:base:1.0"
    final = False  # final node can't have children

    def __init__(self):
        self.children = []
        self.parent = None
        self.operation = None

    def __iter__(self):
        return iter(self.children)

    def __hash__(self):
        return hash(self.path)

    def __cmp__(self, other):
        return cmp(self.path, other.path)

    def add(self, child):
        """Add new child node.
        Doesn't add the child if node with same path already exists.

        :param child: child nde to add
        :return: added child or existing with same path
        """
        if self.final:
            raise ValueError("Can't add child, '%s' is final node." % self.path)
        child.parent = self
        if child not in self.children:
            self.children.append(child)
            return child
        else:
            return self.children[self.children.index(child)]

    def add_removal(self, child):
        """Add new child node marked for removal.

        :param child:
        :return:
        """
        child.operation = "remove"
        return self.add(child)

    def add_replace(self, child):
        """Add a new child node to replace an existing one if it exists.

        :param child:
        :return:
        """
        child.operation = "replace"
        return self.add(child)

    def remove(self, child):
        self.children.remove(child)
        child.parent = None

    def find_child(self, path, where=None):
        """Find child according to path, supports Uci-style indexing for sections.

        :param path: path to the node
        :param where: where to start the search
        :type where: YinElement
        :return: YinElement
        """
        where = where or self
        keys = path.split(".")

        while keys and where:
            key = keys.pop(0)
            if key[0] == "@":
                match = anon_path.match(key)
                section_type = match.group("name")
                sections = filter(lambda x: x.type == section_type, where.children)
                pos = int(match.group("pos"))
                try:
                    where = sections[pos]
                except IndexError:
                    where = None
            else:
                for child in where.children:
                    if child.key == key:
                        where = child
                        break
                else:
                    where = None
        return where

    def _append_subelements(self, element):
        pass

    def to_element(self):
        """Get XML representation of this element.

        :return: Element
        """
        if not self.tag:
            return None
        element = ET.Element(self.qual_tag(self.tag))
        if self.operation:
            element.set(self.qual_tag("operation", YinElement.NS_URI), self.operation)
        self._append_subelements(element)
        return element

    def get_tree(self, subelement=None):
        """Get XML for this node and its parents.

        :param subelement:
        :return: Element
        """
        element = self.to_element()
        if subelement is not None:
            if element is None:
                return subelement
            element.append(subelement)
        if element is None:
            raise ValueError("Node cannot be converted to XML tree, probably trying to serialize node without XML tag.")

        if self.parent:
            return self.parent.get_tree(element)
        else:
            return element

    def get_xml(self):
        """Get XML for this node and all its children.

        :return: Element
        """
        element = self.to_element()
        for child in self.children:
            element.append(child.get_xml())
        return element

    @property
    def path(self):
        parent = self.parent
        path = [self.key]
        while parent is not None:
            if not parent.key:
                break
            path.append(parent.key)
            parent = parent.parent
        return ".".join(reversed(path))

    @property
    def key(self):
        raise NotImplementedError()

    @staticmethod
    def from_element(element):
        """Create new YinElement instance from ElementTree Element.

        :param element: ElementTree Element instance

        :returns: YinElement
        """
        raise NotImplementedError()

    @classmethod
    def qual_tag(cls, tag, ns_uri=None):
        ns_uri = ns_uri or cls.NS_URI
        return "{%s}%s" % (ns_uri, tag)


class Data(YinElement):
    """
    Wrapper class for RPC reply data.
    """
    @property
    def key(self):
        return None


####################################################################################################
ET.register_namespace("nc", YinElement.NS_URI)
