"""
Converter for DMN code into IDP logic

Program turns a DMN table (XML table in essence) into a txt file with IDP code.
"""

import dmnconverter.read.XML
import dmnconverter.transform.implicative
import dmnconverter.transform.inductive
import dmnconverter.transform.meta
import dmnconverter.verify.coverage
import dmnconverter.verify.unique_policy
import dmnconverter.verify.verification
import dmnconverter.learning.tablelearner


class DMNConverter:
    # define used ontology
    ont = '{http://www.omg.org/spec/DMN/20151101/dmn.xsd}'

    def __init__(self):
        return

    def read(self, file_name):
        """
Read DMN table, extract labels and rules and store in this object
        :param file_name:
        """
        try:
            self.dmn_tables = dmnconverter.read.XML.read_tables(file_name)
            self.TableRead = True

        except Exception:
            raise

    def print_inductive(self, file_name):
        """
Create file for direct inductive representation of DMN table
        :param file_name:
        """
        dmnconverter.transform.inductive.InductiveConverter().print_file(file_name, self.dmn_tables)

    def print_implicative(self, file_name):
        """
Create file for direct implicative representation of DMN table
        :param file_name:
        """
        dmnconverter.transform.implicative.ImplicativeConverter().print_file(file_name, self.dmn_tables)

    def print_meta(self, file_name):
        """
Create file for meta representation of DMN table
        :param file_name:
        """
        dmnconverter.transform.meta.MetaConverter().print_file(file_name, self.dmn_tables)

    def verify_coverage(self, file_name):
        """
Create file to check that DMN table fully covers input space
        :param file_name:
        """
        dmnconverter.verify.coverage.Coverage().print_file(file_name, self.dmn_tables)

    def verify_all(self, file_name):
        """
Create file to check that DMN table fully covers input space and has no output conflicts
        :param file_name:
        """
        dmnconverter.verify.verification.Verification().print_file(file_name, self.dmn_tables)

    def verify_unique(self, file_name):
        """
Create file to check that DMN table fully covers input space without overlap (for Unique hit policy)
        :param file_name:
        """
        dmnconverter.verify.unique_policy.VerifyUniquePolicy().print_file(file_name, self.dmn_tables)

    def learn_table(self, file_name):
        dmnconverter.learning.tablelearner.TableLearner().print_file(file_name, self.dmn_tables)

