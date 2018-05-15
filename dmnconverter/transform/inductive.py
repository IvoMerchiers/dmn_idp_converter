
from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.transform.general import DirectConverter


class InductiveConverter(DirectConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        dmn_table = decision_tables[0]
        # read out from structure
        input_rule_comp = dmn_table.input_rule_comp
        output_rule_comp = dmn_table.output_rule_comp
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels

        vocabulary = self.build_vocabulary(dmn_table)

        theory = self.build_theory(input_rule_comp, input_labels, output_rule_comp, output_labels)

        return vocabulary, theory, []

    def build_theory(self, input_rule_comp: list, input_labels: [str], output_rule_comp: list,
                     output_labels: [str]) -> [str]:
        """returns list of string lines representing all the rules in the theory"""
        theory_lines = ['{']
        rules = [
            self.__translate_inductive(input_labels, input_rule_comp[rule_nr], output_labels, output_rule_comp[rule_nr])
            for
            rule_nr in
            range(len(input_rule_comp))]
        theory_lines.extend(rules)
        theory_lines.append('}')
        return theory_lines

    def __translate_inductive(self, input_labels: [str], input_rule_entries: [(str, str)], output_labels: [str],
                              output_rule_entries: [(str, str)]) -> str:
        # TODO: reading out entries can probably be put into super class and combined with implicativeConverter
        """
    Returns a single inductive rule as a string.
        :param input_labels:
        :param input_rule_entries:
        :param output_labels:
        :param output_rule_entries:
        :return:
        """
        rule_string = []
        # Cover outputs
        for i in range(len(output_rule_entries)):
            # check only one output value
            if i > 0:
                raise ValueError('Inductive definition model can currently only have one output entry.')
            # Read specific rule
            if output_rule_entries[i] is not None:
                rule_comparator = output_rule_entries[i][0]
                rule_entry = output_rule_entries[i][1]
                rule_string.append(output_labels[i] + " " + rule_comparator + ' ' + rule_entry)
        rule_string.append(" <- ")

        # Cover input
        for i in range(len(input_rule_entries)):
            if input_rule_entries[i] is not None:
                rule_string.append(self.translate_entry(input_labels[i], input_rule_entries[i]))
                rule_string.append(" & ")
        del rule_string[-1]  # Remove last &
        rule_string.append(".")
        return ''.join(rule_string)
