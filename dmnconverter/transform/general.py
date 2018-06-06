# File contains some translation operations that are more general and are used in multiple representations
import itertools
from abc import ABC, abstractmethod

from boltons.setutils import IndexedSet

import dmnconverter.tools.print as printer
from dmnconverter.tools.decisiontable import DecisionTable


class GeneralConverter(ABC):
    def __init__(self):
        pass

    def print_file(self, file_name, dmn_tables: [DecisionTable]) -> None:
        # Translate vocabulary
        """
        Print table as a txt file in the correct framework
        :param file_name: name of output file
        :param dmn_tables: list of classes containing all info about the current decisiontable
        """
        (vocabulary, theory, structure) = self.convert(dmn_tables)
        printer.print_idp(file_name, vocabulary, theory, structure)

    def print_base_file(self, file_name) -> None:
        """
Prints file without reference to a specific decision table, so voc and theory without a structure.
        :param file_name:
        """
        empty_table = DecisionTable()
        vocabulary = self.build_vocabulary(empty_table)
        theory = self.build_theory(empty_table)
        structure = self.build_structure(empty_table)
        printer.print_idp(file_name, vocabulary, theory, structure)

    @abstractmethod
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        """
Convert a given decision table into the required format
        :rtype: 3-tuple containing vocabulary, theory and structure, each as a list of strings
        :param decision_tables:
        """
        pass

    @abstractmethod
    def build_vocabulary(self, decision_table: DecisionTable) -> [str]:
        pass

    @abstractmethod
    def build_theory(self, decision_table: DecisionTable) -> [str]:
        pass

    @abstractmethod
    def build_structure(self, decision_table: DecisionTable) -> [str]:
        pass


class DirectConverter(GeneralConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):

        vocabularies = [self.build_vocabulary(table) for table in decision_tables]
        vocab_list = list(itertools.chain.from_iterable(vocabularies))
        # remove double entries
        vocabulary = list(IndexedSet(vocab_list))

        theories = [self.build_theory(table) for table in decision_tables]
        theory = list(itertools.chain.from_iterable(theories))

        structures = [self.build_structure(table) for table in decision_tables]
        structure = list(itertools.chain.from_iterable(structures))

        return vocabulary, theory, structure

    def build_vocabulary(self, dmn_table: DecisionTable) -> [str]:
        """
Build the vocabulary for the direct translation
        :param dmn_table: structured version of Decision table
        :return:
        """
        input_label_dict = dmn_table.input_label_dict
        output_label_dict = dmn_table.output_label_dict

        # vocabulary uses the more general direct translation
        vocabulary = ["//Input variables"]
        vocabulary.extend(self.__direct_voc(input_label_dict))
        vocabulary.append('//Output variables')
        vocabulary.extend(self.__direct_voc(output_label_dict))
        return vocabulary

    @abstractmethod
    def build_theory(self, decision_table: DecisionTable) -> [str]:
        pass

    def build_structure(self, decision_table: DecisionTable) -> [str]:
        return []

    def __direct_voc(self, labels_dict: dict) -> list:
        """Turns a dictionary of labels into a direct translation of the vocabulary
        :param labels_dict: dictionary of labels
        :return: list of strings, every entry is a line in the vocabulary
        """
        voc_lines = []
        for key in labels_dict.keys():
            voc_lines.extend(self.__single_expression2voc(key, labels_dict[key]))
        return voc_lines

    @staticmethod
    def __single_expression2voc(label: str, value_tuple: tuple) -> list:
        """
    Returns the correct lines in the direct vocabulary for a single expression (variable).
        :param label:
        :param value_tuple:
        :return: list of 2 strings, the definition of the type labelEntry and the function of that label
        """
        type_ref = value_tuple[0]
        values = value_tuple[1]
        if type_ref in ['string', 'boolean']:
            voc_entry_line = 'type ' + label + '_entry constructed from {' + values + '}'
        elif type_ref in ['integer']:
            voc_entry_line = 'type ' + label + '_entry isa int'
        else:
            raise TypeError("type " + type_ref + ' unknown')
        voc_function_line = label + '():' + label + '_entry'
        return [voc_entry_line, voc_function_line]

    @staticmethod
    def translate_entry(label: str, rule_entry: tuple) -> str:
        """
translates one entry in the direct formalism
        :param label:
        :param rule_entry:
        :return:
        """
        entry_strings = []
        rule_comparator = rule_entry[0]
        rule_entry = rule_entry[1]
        rule_cases = rule_entry.split(", ")
        for case in rule_cases:
            entry_strings.append(label + " " + rule_comparator + " " + case)
            entry_strings.append(" | ")
        # delete last or case
        del entry_strings[-1]
        return ''.join(entry_strings)
