from abc import abstractmethod

from boltons.setutils import IndexedSet

from dmnconverter.tools import texttools as text_tools
from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.transform.general import GeneralConverter


class MetaLanguageConverter(GeneralConverter):
    @abstractmethod
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        pass

    def build_structure(self, decision_table: DecisionTable) -> [str]:
        """
Builds meta representation structure based on the dictionary representation of the structure
        :param decision_table:
        :return:
        """
        structure_dict = self.build_structure_dict(decision_table)
        predicate_names = structure_dict.keys()
        structure: [str] = []
        for predicate in predicate_names:
            value_list = structure_dict[predicate]
            # remove doubles
            unique_value_list = list(IndexedSet(value_list))
            values_string = '; '.join(unique_value_list)
            structure.append(predicate + " = {" + values_string + "}")
        return structure

    @abstractmethod
    def build_structure_dict(self, dmn_table: [DecisionTable]) -> dict:
        """
Stores all elements of the structure as key='predicate', value='values of string'
        :param dmn_table:
        """
        pass

    @staticmethod
    def structure_variables(dmn_table: DecisionTable) -> ([str], [str]):
        """
Reads out input and output variables from a DecisionTable for usage in the structure
        :param dmn_table: DecisionTable object
        :return: tuple of lists of strings indicating respectively input and output variables
        """
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels

        input_variables = text_tools.enquote_list(input_labels)
        output_variables = text_tools.enquote_list(output_labels)

        return input_variables, output_variables

    @staticmethod
    def list_meta_variables(labels: list) -> str:
        """
Quotes and ';'-joins a list of labels
        :param labels:
        :return:
        """
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

    def build_meta_input_rule(self, dmn_table: DecisionTable) -> [str]:
        """
        Make list of all rule components, ready to be entered in the IDP structure (still needs ";" separation
        between elements) :param dmn_table: :return:
        """
        labels = dmn_table.input_labels
        rule_components = dmn_table.input_rule_comp

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

    @staticmethod
    def build_output_rule(dmn_table: DecisionTable) -> [str]:
        labels = dmn_table.output_labels
        rule_components = dmn_table.output_rule_comp

        rule = []
        amount_entries = len(labels)
        enquoted_labels = text_tools.enquote_list(labels)

        for rule_nr in range(len(rule_components)):
            rule_component = rule_components[rule_nr]
            for entry_nr in range(amount_entries):
                entry = rule_component[entry_nr]
                if entry is not None:
                    label = enquoted_labels[entry_nr]
                    (comparator, value) = entry
                    # enquote non integer values
                    try:
                        int(value)
                    except ValueError:
                        value = text_tools.enquote(value)
                    rule.append(str(rule_nr + 1) + ',' + label + ',' + value)
        return rule
