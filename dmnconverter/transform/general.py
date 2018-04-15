# File contains some translation operations that are more general and are used in multiple representations
from dmnconverter.tools import texttools as text_tools


def direct_voc(labels_dict: dict) -> list:
    """Turns a dictionary of labels into a direct translation of the vocabulary
    :param labels_dict: dictionary of labels
    :return: list of strings, every entry is a line in the vocabulary
    """
    voc_lines = [__single_expression2voc(key, labels_dict[key]) for key in labels_dict.keys()]
    return voc_lines


def __single_expression2voc(label: str, value_tuple: tuple) -> str:
    type_ref = value_tuple[0]
    values = value_tuple[1]
    if type_ref in ['string', 'boolean']:
        voc_line = 'type ' + label + ' constructed from {' + values + '}'
    elif type_ref in ['integer']:
        voc_line = 'type ' + label + ' isa int'
    else:
        raise TypeError("type " + type_ref + ' unknown')
    return voc_line


def list_meta_variables(labels: list) -> str:
    listing = '; '.join(labels)
    return listing



def encode_comparison(comparator: str) -> str:
    """
Translate symbolic representation of comparison operators to (shorthand) names used in the meta representation
    :param comparator:
    :return:
    """
    encoding = {'=': 'eq()', '<': 'less()', '=<': 'leq()', '>': 'gtr()', '>=': 'geq()'}
    return encoding[comparator]


def specify_meta_domain(label_dict: dict, range_start: int, range_stop: int) -> tuple:
    """
Determine domain and range of variables in the dictionary
    :param label_dict:
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


def build_meta_input_rule(labels: list, rule_components: list) -> list:
    """
Make list of all rule components, ready to be entered in the IDP structure (with ";" separation between elements)
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
                rule.extend(__build_single_input_entry(rule_nr + 1, label, comparator, value))

    return rule

def __build_single_input_entry(rule_nr: int, label: str, comparator: str, value: str) -> list:
    # case of range (transform into 2 rules and recursively deal with them)
    if comparator.startswith(('[', ']')):
        first_dict = {'[': '>=', ']': '>'}
        last_dict = {'[': '<', ']': '=<'}

        inclusion_symbols = comparator
        values = value.split('..')

        # recursive call
        first_rule_comp = __build_single_input_entry(rule_nr, label, first_dict[inclusion_symbols[0]], values[0])
        second_rule_comp = __build_single_input_entry(rule_nr, label, last_dict[inclusion_symbols[1]], values[1])

        entry = first_rule_comp + second_rule_comp

    else:
        comparator_name = encode_comparison(comparator)
        # enquote non integer values
        try:
            int(value)
        except ValueError:
            value = text_tools.enquote(value)
        entry = [str(rule_nr) + ',' + label + ',' + comparator_name + ',' + value]
    return entry
