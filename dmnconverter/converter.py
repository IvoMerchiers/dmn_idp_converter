"""
Converter for DMN code into IDP logic

Program turns a DMN table (XML table in essence) into a txt file with IDP code.
"""

import xml.etree.ElementTree as ElemTree
import dmnconverter.read.XML
import dmnconverter.transform.inductive
import dmnconverter.transform.implicative
import dmnconverter.transform.meta
import dmnconverter.verify.unique_policy


class DMNConverter:
    # define used ontology
    ont = '{http://www.omg.org/spec/DMN/20151101/dmn.xsd}'

    def __init__(self):
        return

    def read(self, file_name):
        """Read DMN table, extract labels and rules"""
        try:
            self.dmn_tables = dmnconverter.read.XML.read_tables(file_name)
            self.TableRead = True

        except Exception as e:
            raise

    def print_inductive(self, file_name):
        dmnconverter.transform.inductive.InductiveConverter().print_file(file_name, self.dmn_tables)

    def print_implicative(self, file_name):
        dmnconverter.transform.implicative.ImplicativeConverter().print_file(file_name, self.dmn_tables)

    def print_meta(self, file_name):
        dmnconverter.transform.meta.MetaConverter().print_file(file_name, self.dmn_tables)

    def verify_unique(self, file_name):
        dmnconverter.verify.unique_policy.UniquePolicy().print_file(file_name, self.dmn_tables)

