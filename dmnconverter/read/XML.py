from dmnconverter.tools.textclean import clean_text
import re


def read_expressions(ont: str, dec_table, category: str) -> dict:
    """ Read the expressions from the DMN table
    :param ont: used ontology
    :param dec_table: relevant decision table
    :param category: either 'input' or 'output'
    :return: dictionary with key every expression and a tuple of (typeRef, values), with values a string
    """
    labels_dict = dict()
    for expression in dec_table.findall(ont + category):
        label = expression.attrib['label']
        label = label.replace(' ', '_')
        values = __read_values(ont, category, expression)  # type: tuple (typeRef, values)

        labels_dict[label] = values
    return labels_dict


def __read_values(ont: str, category: str, expression) -> tuple:
    """Returns tuple of 'type_ref' and 'values'"""
    # Find type
    if category == 'input':
        type_ref = expression.find(ont + category + 'Expression').attrib['typeRef']
    elif category == 'output':
        type_ref = expression.attrib['typeRef']
    else:
        raise ValueError('Input category ' + str(category) + ' not recognized')

    # Act accordingly
    if type_ref == 'string':
        values = clean_text(expression.find(ont + category + 'Values'))
    elif type_ref == 'boolean':
        values = 'true,false'
    elif type_ref == 'integer':
        values = 'int'
    else:
        raise ValueError('Type ' + type_ref + ' not yet implemented or not recognized.')
    return type_ref, values


def read_rules(ont: str, dec_table) -> "Tuple of lists":
    """Rules stored as tuple of 2 2D Matrix of entries. First matrix is input, second is output
    :param ont: Ontology
    used in the decision table
    :param dec_table: relevant decision table
    :return: tuple of input and output rule
    components. These are two lists, representing every rule entry, where the first index iterates over the rules and
    second index over the value assigned to that variable. The assigned value is in the form of a (comparator,
    value) tuple  or None if no comparison is made.
    """
    # Find list of rules
    dmn_rules = dec_table.findall(ont + 'rule')
    # Read input and output entries of all the rules. While doing string cleanup
    input_rule_comp = [[__structure_comparison(entry) for entry in rule.findall(ont + 'inputEntry')] for rule in
                       dmn_rules]
    output_rule_comp = [[__structure_comparison(entry) for entry in rule.findall(ont + 'outputEntry')] for rule in
                        dmn_rules]

    return input_rule_comp, output_rule_comp


def __structure_comparison(entry: "XML inputEntry") -> (str, str):
    """
    Reads one rule-entry and structures it as a tuple consisting of (comparator, value), both encoded as strings.
    Returns None if no entry is present
    :param entry: The XML inputEntry as defined in the ontology
    :return:
    """
    cleaned = clean_text(entry)
    if cleaned is None:
        return cleaned
    content_pattern = re.compile('[\\w.]+')
    content_match = re.search(content_pattern, cleaned)
    content = content_match.group(0)

    comparator = cleaned.replace(content, '')
    if not comparator:
        comparator = '='
    elif comparator == '<=':
        comparator = '=<'

    content = content.strip('_')  # removes excess underscores
    return comparator, content
