import dmnconverter.tools.print as printer
import dmnconverter.transform.general


def print_file(file_name, input_rule_comp: list, input_label_dict: dict,
               output_rule_comp: list, output_label_dict: dict) -> None:
    # Translate vocabulary
    """
    Print table as a txt file in the implicative framework
    :param file_name: name of output file
    :param input_rule_comp: 2d array of rule components
    :param input_label_dict: dictionary of labels and the tuple indicating their domain
    :param output_rule_comp: 2d array of output rule comps
    :param output_label_dict: dictionary of output labels and their domains
    """
    # vocabulary uses the more general direct translation
    vocabulary = ["//Input entries with labels"]
    vocabulary.extend(dmnconverter.transform.general.direct_voc(input_label_dict))
    vocabulary.append('//Output entries')
    vocabulary.extend(dmnconverter.transform.general.direct_voc(output_label_dict))

    # Find output labels
    input_labels = list(input_label_dict.keys())
    output_labels = list(output_label_dict.keys())
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


def __translate_implicative(input_labels: [str], input_rule_entries: list, output_labels: [str], output_rule_entries: list) -> str:
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
            rule_comparator=input_rule_entries[i][0]
            rule_entry = input_rule_entries[i][1]
            rule_string.append(input_labels[i] +' '+ rule_comparator +' '+ rule_entry)
            rule_string.append(" & ")
    del rule_string[-1]  # remove last &
    rule_string.append(" => ")

    # cover output
    for i in range(len(output_rule_entries)):
        # Read specific rule
        if output_rule_entries[i] is not None:
            rule_comparator = output_rule_entries[i][0]
            rule_entry = output_rule_entries[i][1]
            rule_string.append(output_labels[i] + " "+ rule_comparator + ' ' + rule_entry)
            rule_string.append(" & ")
    del rule_string[-1]
    return ''.join(rule_string)