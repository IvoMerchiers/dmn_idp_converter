import dmnconverter.tools.print as printer

def print_file(file_name, input_rule_comp: list, input_label_dict: dict,
               output_rule_comp: list, output_label_dict: dict) -> None:
    # Translate vocabulary
    """
    Print table as a txt file in the meta framework. This means all info about specific dec table
    is in the structure.
    :param file_name: name of output file
    :param input_rule_comp: 2d array of rule components
    :param input_label_dict: dictionary of labels and the tuple indicating their domain
    :param output_rule_comp: 2d array of output rule comps
    :param output_label_dict: dictionary of output labels and their domains
    """
    # vocabulary is fixed
    vocabulary = ["//Input entries with labels"]
    vocabulary.extend(dmnconverter.transform.general.direct_voc(input_label_dict))
    vocabulary.append('//Output entries')
    vocabulary.extend(dmnconverter.transform.general.direct_voc(output_label_dict))

    # Find output labels
    input_labels = list(input_label_dict.keys())
    output_labels = list(output_label_dict.keys())
    # Theory is fixed
    theory = __rules2theory(input_rule_comp, input_labels, output_rule_comp, output_labels)
    # print results


    #
    printer.print_idp(file_name, vocabulary, theory)