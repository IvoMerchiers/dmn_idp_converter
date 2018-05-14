import dmnconverter.tools.print as printer
import dmnconverter.transform.general
from dmnconverter.tools.decisiontable import DecisionTable


def print_file(file_name, dmn_table: DecisionTable) -> None:
    # Translate vocabulary
    """
    Print table as a txt file in the implicative framework
    :param file_name: name of output file
    :param dmn_table: class containing all info about the current decisiontable
    """
    # read out from structure
    input_label_dict = dmn_table.input_label_dict
    output_label_dict = dmn_table.output_label_dict
    input_rule_comp = dmn_table.input_rule_comp
    output_rule_comp = dmn_table.output_rule_comp
    input_labels = dmn_table.input_labels
    output_labels = dmn_table.output_labels

    # vocabulary uses the more general direct translation
    vocabulary = ["//Input variables"]
    vocabulary.extend(dmnconverter.transform.general.direct_voc(input_label_dict))
    vocabulary.append('//Output variables')
    vocabulary.extend(dmnconverter.transform.general.direct_voc(output_label_dict))

    # Translate theory
    theory = __rules2theory(input_rule_comp, input_labels, output_rule_comp, output_labels)
    # print results
    printer.print_idp(file_name, vocabulary, theory, [])


def __rules2theory(input_rule_comp: list, input_labels: list, output_rule_comp: list, output_labels: list):
    """returns list of string lines representing all the rules in the theory"""
    theory_lines = []
    for i in range(len(input_rule_comp)):  # loop over all rules
        theory_lines.append(
            __translate_implicative(input_labels, input_rule_comp[i], output_labels,
                                    output_rule_comp[i]))
    return theory_lines


def __translate_implicative(input_labels: [str], input_rule_entries: [tuple], output_labels: [str],
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
            rule_string.append(__translate_entry(input_labels[i], input_rule_entries[i]))
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


def __translate_entry(label: str, rule_entry: tuple) -> str:
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
