# File contains some translation operations that are more general and are used in multiple representations
import itertools
import deprecation

from dmnconverter.tools import texttools as text_tools
from abc import ABC, abstractmethod

from dmnconverter.tools.decisiontable import DecisionTable
import dmnconverter.tools.print as printer
from boltons.setutils import IndexedSet


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

    def __direct_voc(self, labels_dict: dict) -> list:
        """Turns a dictionary of labels into a direct translation of the vocabulary
        :param labels_dict: dictionary of labels
        :return: list of strings, every entry is a line in the vocabulary
        """
        # voc_lines = [__single_expression2voc(key, labels_dict[key]) for key in labels_dict.keys()]
        voc_lines = []
        for key in labels_dict.keys():
            voc_lines.extend(self.__single_expression2voc(key, labels_dict[key]))
        return voc_lines

    @abstractmethod
    def build_theory(self, decision_table: DecisionTable) -> [str]:
        pass

    def build_structure(self, decision_table: DecisionTable) -> [str]:
        return []

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
        voc_function_line = label + ':' + label + '_entry'
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


class MetaLanguageConverter(GeneralConverter):
    @abstractmethod
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        pass

    def structure_variables(self, dmn_table: DecisionTable) -> ([str], [str]):
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels

        input_variables = text_tools.enquote_list(input_labels)
        output_variables = text_tools.enquote_list(output_labels)

        return input_variables, output_variables

    @staticmethod
    def list_meta_variables(labels: list) -> str:
        listing = '; '.join(text_tools.enquote_list(labels))
        return listing

    @staticmethod
    def encode_comparison(comparator: str) -> str:
        """
    Translate symbolic representation of comparison operators to (shorthand) names used in the meta representation
        :param comparator:
        :return:
        """
        encoding = {'=': 'eq()', '<': 'less()', '=<': 'leq()', '>': 'gtr()', '>=': 'geq()'}
        return encoding[comparator]

    @staticmethod
    def specify_meta_domain(label_dict: dict, range_start: int, range_stop: int) -> tuple:
        """
    Determine domain and range of variables in the dictionary
        :param label_dict: dictionary of labels and domains
        :param range_start:
        :param range_stop:
        :return: tuple of all Domain and Ranges that are associated to this dictionary (list(str),list(str))
        """
        domain = []
        ranges = []

        keys = label_dict.keys()
        for key in keys:
            current_variable = text_tools.enquote(str(key))
            (type_ref, values) = label_dict[key]

            if type_ref in ['string', 'boolean']:
                value_list = values.split(',')
                domain.extend([current_variable + ',' + value for value in text_tools.enquote_list(value_list)])
            elif type_ref in ['integer']:
                ranges.append(current_variable + ',' + str(range_start) + ',' + str(range_stop))
            else:
                raise TypeError('Unknown type ' + str('type_ref'))
        return domain, ranges

    def build_meta_input_rule(self, labels: list, rule_components: list) -> [str]:
        """
    Make list of all rule components, ready to be entered in the IDP structure (still needs ";" separation between elements)
        :param labels:
        :param rule_components:
        :return:
        """
        rule = []
        amount_entries = len(labels)
        enquoted_labels = text_tools.enquote_list(labels)

        # note rule_nr is one index off from what IDP uses (therefore +1 later on)
        for rule_nr in range(len(rule_components)):
            rule_component = rule_components[rule_nr]
            for entry_nr in range(amount_entries):
                entry = rule_component[entry_nr]
                if entry is not None:
                    label = enquoted_labels[entry_nr]
                    (comparator, value) = entry
                    rule.extend(self.__build_single_input_rule(rule_nr + 1, label, comparator, value))

        return rule

    def __build_single_input_rule(self, rule_nr: int, label: str, comparator: str, value: str) -> [str]:
        # case of range (transform into 2 rules and recursively deal with them)
        if comparator.startswith(('[', ']')):
            first_dict = {'[': '>=', ']': '>'}
            last_dict = {'[': '<', ']': '=<'}

            inclusion_symbols = comparator
            values = value.split('..')

            # recursive call
            first_rule_comp = self.__build_single_input_rule(rule_nr, label, first_dict[inclusion_symbols[0]],
                                                             values[0])
            second_rule_comp = self.__build_single_input_rule(rule_nr, label, last_dict[inclusion_symbols[1]],
                                                              values[1])

            entry = first_rule_comp + second_rule_comp

        else:
            entry = []
            comparator_name = self.encode_comparison(comparator)
            rule_cases = value.split(", ")
            # deal with multiple cases
            for i in range(len(rule_cases)):
                case = rule_cases[i]
                case_nr = i + 1
                # enquote non integer values
                try:
                    int(case)
                except ValueError:
                    case = text_tools.enquote(case)
                entry.append(str(rule_nr) + ',' + str(case_nr) + ',' + label + ',' + comparator_name + ',' + case)
        return entry


# TODO: clean up the following methods, since depricated in classes
# def direct_voc(labels_dict: dict) -> list:
#     """Turns a dictionary of labels into a direct translation of the vocabulary
#     :param labels_dict: dictionary of labels
#     :return: list of strings, every entry is a line in the vocabulary
#     """
#     # voc_lines = [__single_expression2voc(key, labels_dict[key]) for key in labels_dict.keys()]
#     voc_lines = []
#     for key in labels_dict.keys():
#         voc_lines.extend(__single_expression2voc(key, labels_dict[key]))
#     return voc_lines
#
#
# def __single_expression2voc(label: str, value_tuple: tuple) -> list:
#     """
# Returns the correct lines in the direct vocabulary for a single expression (variable).
#     :param label:
#     :param value_tuple:
#     :return: list of 2 strings, the definition of the type labelEntry and the function of that label
#     """
#     type_ref = value_tuple[0]
#     values = value_tuple[1]
#     if type_ref in ['string', 'boolean']:
#         voc_entry_line = 'type ' + label + '_entry constructed from {' + values + '}'
#     elif type_ref in ['integer']:
#         voc_entry_line = 'type ' + label + '_entry isa int'
#     else:
#         raise TypeError("type " + type_ref + ' unknown')
#     voc_function_line = label + ':' + label + '_entry'
#     return [voc_entry_line, voc_function_line]
#
#
# def list_meta_variables(labels: list) -> str:
#     listing = '; '.join(labels)
#     return listing
#
#
# def encode_comparison(comparator: str) -> str:
#     """
# Translate symbolic representation of comparison operators to (shorthand) names used in the meta representation
#     :param comparator:
#     :return:
#     """
#     encoding = {'=': 'eq()', '<': 'less()', '=<': 'leq()', '>': 'gtr()', '>=': 'geq()'}
#     return encoding[comparator]
#
#
# def specify_meta_domain(label_dict: dict, range_start: int, range_stop: int) -> tuple:
#     """
# Determine domain and range of variables in the dictionary
#     :param label_dict:
#     :return: tuple of all Domain and Ranges that are associated to this dictionary (list(str),list(str))
#     """
#     domain = []
#     ranges = []
#
#     keys = label_dict.keys()
#     for key in keys:
#         current_variable = text_tools.enquote(str(key))
#         (type_ref, values) = label_dict[key]
#
#         if type_ref in ['string', 'boolean']:
#             value_list = values.split(',')
#             domain.extend([current_variable + ',' + value for value in text_tools.enquote_list(value_list)])
#         elif type_ref in ['integer']:
#             ranges.append(current_variable + ',' + str(range_start) + ',' + str(range_stop))
#         else:
#             raise TypeError('Unknown type ' + str('type_ref'))
#     return domain, ranges
#
#
# def build_meta_input_rule(labels: list, rule_components: list) -> list:
#     """
# Make list of all rule components, ready to be entered in the IDP structure (still needs ";" separation between elements)
#     :param labels:
#     :param rule_components:
#     :return:
#     """
#     rule = []
#     amount_entries = len(labels)
#     enquoted_labels = text_tools.enquote_list(labels)
#
#     # note rule_nr is one index off from what IDP uses (therefore +1 later on)
#     for rule_nr in range(len(rule_components)):
#         rule_component = rule_components[rule_nr]
#         for entry_nr in range(amount_entries):
#             entry = rule_component[entry_nr]
#             if entry is not None:
#                 label = enquoted_labels[entry_nr]
#                 (comparator, value) = entry
#                 rule.extend(__build_single_input_rule(rule_nr + 1, label, comparator, value))
#
#     return rule
#
#
# def __build_single_input_rule(rule_nr: int, label: str, comparator: str, value: str) -> [str]:
#     # case of range (transform into 2 rules and recursively deal with them)
#     if comparator.startswith(('[', ']')):
#         first_dict = {'[': '>=', ']': '>'}
#         last_dict = {'[': '<', ']': '=<'}
#
#         inclusion_symbols = comparator
#         values = value.split('..')
#
#         # recursive call
#         first_rule_comp = __build_single_input_rule(rule_nr, label, first_dict[inclusion_symbols[0]], values[0])
#         second_rule_comp = __build_single_input_rule(rule_nr, label, last_dict[inclusion_symbols[1]], values[1])
#
#         entry = first_rule_comp + second_rule_comp
#
#     else:
#         entry = []
#         comparator_name = encode_comparison(comparator)
#         rule_cases = value.split(", ")
#         # deal with multiple cases
#         for i in range(len(rule_cases)):
#             case = rule_cases[i]
#             case_nr = i + 1
#             # enquote non integer values
#             try:
#                 int(case)
#             except ValueError:
#                 case = text_tools.enquote(case)
#             entry.append(str(rule_nr) + ',' + str(case_nr) + ',' + label + ',' + comparator_name + ',' + case)
#     return entry
