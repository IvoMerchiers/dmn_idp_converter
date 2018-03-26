from dmnconverter.tools.textclean import clean_text
import re


def read_expressions(ont: str, dec_table, category: str) -> dict:
    """Category can be 'input' or 'output'"""
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
    """Rules stored as tuple of 2 2D Matrix of entries. First matrix is input, second is output """
    # Find list of rules
    dmn_rules = dec_table.findall(ont + 'rule')
    # Read input and output entries of all the rules. While doing string cleanup
    input_rule_comp = [[__structure_comparison(entry) for entry in rule.findall(ont + 'inputEntry')] for rule in
                       dmn_rules]
    output_rule_comp = [[__structure_comparison(entry) for entry in rule.findall(ont + 'outputEntry')] for rule in
                        dmn_rules]
    return input_rule_comp, output_rule_comp


def __structure_comparison(entry: "XML inputEntry") -> (str, str):
    # clean
    cleaned = clean_text(entry)
    if cleaned is None:
        return cleaned
    content_pattern = re.compile('[\\w]+')
    content_match = re.search(content_pattern, cleaned)
    content = content_match.group(0)

    comparator = cleaned.replace(content, '')
    if not comparator:
        comparator = '='
    elif comparator == '<=':
        comparator = '=<'

    content = content.strip('_')  # removes excess underscores
    return comparator, content
