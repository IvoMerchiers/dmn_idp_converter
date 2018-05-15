from dmnconverter.transform.general import DirectConverter
from dmnconverter.tools.decisiontable import DecisionTable


class ImplicativeConverter(DirectConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        dmn_table = decision_tables[0]
        # read out from structure
        input_rule_comp = dmn_table.input_rule_comp
        output_rule_comp = dmn_table.output_rule_comp
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels

        vocabulary = self.build_vocabulary(dmn_table)

        # Translate theory
        theory = self.build_theory(input_rule_comp, input_labels, output_rule_comp, output_labels)
        # print results
        return vocabulary, theory, []

    def build_theory(self, input_rule_comp: list, input_labels: list, output_rule_comp: list, output_labels: list):
        """returns list of string lines representing all the rules in the theory"""
        theory_lines = []
        for i in range(len(input_rule_comp)):  # loop over all rules
            theory_lines.append(
                self.__translate_implicative(input_labels, input_rule_comp[i], output_labels,
                                             output_rule_comp[i]))
        return theory_lines

    def __translate_implicative(self, input_labels: [str], input_rule_entries: [tuple], output_labels: [str],
                                output_rule_entries: list) -> str:
        """
    Translates one rule into a string
        :param input_labels:
        :param input_rule_entries:
        :param output_labels:
        :param output_rule_entries:
        :return:
        """
        rule_string = []
        # Cover input
        for i in range(len(input_rule_entries)):
            if input_rule_entries[i] is not None:
                rule_string.append(self.translate_entry(input_labels[i], input_rule_entries[i]))
                # rule_comparator = input_rule_entries[i][0]
                # rule_entry = input_rule_entries[i][1]
                # rule_string.append(input_labels[i] + ' ' + rule_comparator + ' ' + rule_entry)
                rule_string.append(" & ")
        del rule_string[-1]  # remove last &
        rule_string.append(" => ")

        # cover output
        for i in range(len(output_rule_entries)):
            # Read specific rule
            if output_rule_entries[i] is not None:
                rule_comparator = output_rule_entries[i][0]
                rule_entry = output_rule_entries[i][1]
                rule_string.append(output_labels[i] + " " + rule_comparator + ' ' + rule_entry)
                rule_string.append(" & ")
        # delete last & and put a dot on the end
        del rule_string[-1]
        rule_string.append(".")

        return ''.join(rule_string)
