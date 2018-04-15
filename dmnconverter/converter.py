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
            # Read and parse tree
            tree = ElemTree.parse(file_name)
            root = tree.getroot()
            table_name = root.find(self.ont + 'decision').attrib['name']
            dec_table = root.find(self.ont + 'decision').find(self.ont + 'decisionTable')

            self.inputLabelDict = dmnconverter.read.XML.read_expressions(self.ont, dec_table, 'input')
            self.outputLabelDict = dmnconverter.read.XML.read_expressions(self.ont, dec_table, 'output')
            self.inputLabels = list(self.inputLabelDict.keys())  # use these?
            self.outputLabels = list(self.outputLabelDict.keys())

            rules=dmnconverter.read.XML.read_rules(self.ont, dec_table)
            self.inputRuleComp = rules[0]
            self.outputRuleComp = rules[1]
            self.TableRead = True

        except Exception as e:
            raise

    def print_inductive(self, file_name):
        dmnconverter.transform.inductive.print_file(file_name, self.inputRuleComp, self.inputLabelDict, self.outputRuleComp, self.outputLabelDict)

    def print_implicative(self, file_name):
        dmnconverter.transform.implicative.print_file(file_name, self.inputRuleComp, self.inputLabelDict, self.outputRuleComp, self.outputLabelDict)

    def print_meta(self, file_name):
        dmnconverter.transform.meta.print_file(file_name, self.inputRuleComp, self.inputLabelDict, self.outputRuleComp, self.outputLabelDict)

    def verify_unique(self, file_name):
        dmnconverter.verify.unique_policy.print_file(file_name, self.inputRuleComp, self.inputLabelDict)

