# File contains some translation operations that are more general and are used in multiple representations
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


def transform_single_entry(label: str, rule_entry: tuple) -> list:
    rule_comparator = rule_entry[0]
    rule_entry_value = rule_entry[1]

    if rule_entry_value is None:
        return None
    elif rule_comparator.startswith(('[', ']')):
        raise ValueError('Range not yet supported')
    else:
        entry_string = label + ' ' + rule_comparator + ' ' + rule_entry_value


def encode_comparison(comparator: str) -> str:
    """
Translate symbolic representation of comparison operators to (shorthand) names used in the meta representation
    :param comparator:
    :return:
    """
    encoding = {'=': 'eq()', '<': 'less()', '=<': 'leq()', '>': 'gtr()', '>=': 'geq()'}
    return encoding[comparator]
