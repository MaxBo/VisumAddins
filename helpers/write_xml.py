# -*- coding: utf8 -*-

import sys
import add_pythonpackages_to_path

from lxml import etree


class VisumXMLProcedures(object):

    def __init__(self, filename):
        """
        Create an xml document

        Parameters
        ----------
        filename : str
        """
        self.filename = filename
        self.root = etree.Element('PROCEDURES')
        self.root.attrib['VERSION'] = '14'

    def write_xml(self):
        with open(self.filename,"w") as f:
            if sys.version_info.major == 3:
                tostring = etree.tounicode
            else:
                tostring = etree.tostring
            f.write(tostring(self.root, pretty_print=True))

    def add_dict_to_node(self, parent, d):
        """
        add the nodes defined in the dict (of dicts) to the parent

        Parameters
        ----------
        parent : etree-Element or str
            the parent node. If a string is given,
            then the first node found in the tree will be used
            if no element with the name is given, a ValueError is raised
        d : dict
            the dict that defines the tree to add to the parent node
        """
        if not isinstance(parent, etree._Element):
            found = self.root.xpath('..//{}'.format(parent))
            if not found:
                raise ValueError('Node {} not found  in tree'.format(parent))
            parent = found[0]

        for k, v in d.items():
            if isinstance(v, dict):
                node = etree.SubElement(parent, k)
                self.add_dict_to_node(node, v)
            elif isinstance(v,list):
                for item in v:
                    node = etree.SubElement(parent, k)
                    self.add_dict_to_node(node, item)
            elif k == "__text__":
                    parent.text = v
            elif k == "__tail__":
                    parent.tail = v
            else:
                parent.set(k, v)


if __name__ == '__main__':
    xml = VisumXMLProcedures(filename=r'C:\temp\a.xml')
    xml.add_functions()
    xml.add_operations()
    xml.write_xml()
