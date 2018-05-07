import dmnconverter.tools.print as printer
import dmnconverter.transform.general


def print_file(file_name, input_rule_comp: list, input_label_dict: dict,
               output_rule_comp: list, output_label_dict: dict) -> None:
    """
    Print table as an idp file in the inductive framework
    :param file_name: name of output file
    :param input_rule_comp: 2d array of rule components
    :param input_label_dict: dictionary of labels and the tuple indicating their domain
    :param output_rule_comp: 2d array of output rule comps
    :param output_label_dict: dictionary of output labels and their domains
    """
    # vocabulary uses the more general direct translation
    vocabulary = ["//Input Variables"]
    vocabulary.extend(dmnconverter.transform.general.direct_voc(input_label_dict))
    vocabulary.append('//Output Variables')
    vocabulary.extend(dmnconverter.transform.general.direct_voc(output_label_dict))

    # Find output labels
    input_labels = list(input_label_dict.keys())
    output_labels = list(output_label_dict.keys())
    # Translate theory
    theory = __rules2theory(input_rule_comp, input_labels, output_rule_comp, output_labels)
    # print results
    printer.print_idp(file_name, vocabulary, theory, [])


def __rules2theory(input_rule_comp: list, input_labels: [str], output_rule_comp: list, output_labels: [str]) -> [str]:
    """returns list of string lines representing all the rules in the theory"""
    theory_lines = ['{']
    rules = [__translate_inductive(input_labels, input_rule_comp[rule_nr], output_labels, output_rule_comp[rule_nr]) for
             rule_nr in
             range(len(input_rule_comp))]
    theory_lines.extend(rules)
    theory_lines.append('}')
    return theory_lines


def __translate_inductive(input_labels: [str], input_rule_entries: [(str, str)], output_labels: [str],
                          output_rule_entries: [(str, str)]) -> str:
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
            rule_string.append(__translate_entry(input_labels[i], input_rule_entries[i]))
            rule_string.append(" & ")
    del rule_string[-1]  # Remove last &
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
