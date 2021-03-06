from dmnconverter.tools.texttools import clean_text
from dmnconverter.tools.decisiontable import DecisionTable

import xml.etree.ElementTree as ElemTree
import re


# FIXME: fix non-deterministic behaviour of 'find'!

def read_tables(file_name: str, ontology: str = '{http://www.omg.org/spec/DMN/20151101/dmn.xsd}') -> [DecisionTable]:
    """
Reads out a dmn table stored as XML file and returns it as a list of decisiontables
    :param file_name: complete file path or relative to call location
    :param ontology: used ontology in the XML table
    :return: list of DecisionTable objects
    """
    tree = ElemTree.parse(file_name)
    root = tree.getroot()
    decisions = root.findall(ontology + 'decision')  # this is defined in the XML structure
    return [read_table(decision, ontology) for decision in decisions]


def read_table(decision, ontology: str) -> DecisionTable:
    """
Reads out a given dmn table.
    :param decision: Defined in XML structure, contains both meta info about the decision table and the actual table.
    :param ontology: ontology used in the proces
    :return: DecisionTable object
    """
    table_name = decision.attrib['name']
    dec_table = decision.find(ontology + 'decisionTable')
    hit_policy = __read_hit_policy(dec_table)
    input_label_dict = read_expressions(ontology, dec_table, 'input')
    output_label_dict = read_expressions(ontology, dec_table, 'output')
    rules = read_rules(ontology, dec_table)
    input_rule_comp = rules[0]
    output_rule_comp = rules[1]
    return DecisionTable(ontology, table_name, hit_policy, input_label_dict, output_label_dict, input_rule_comp, output_rule_comp)


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
        values = 'True,False'
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
    content_pattern = re.compile('[ \\w,]+')

    content_match = re.search(content_pattern, cleaned)

    content = content_match.group(0)

    comparator = cleaned.replace(content, '')
    if not comparator:
        comparator = '='
    elif comparator == '<=':
        comparator = '=<'

    content = content.strip('_')  # removes excess underscores
    content = content.title()  # standardize capitalization
    return comparator, content


def __read_hit_policy(dec_table) ->str:

    try:
        hit_policy: str = dec_table.attrib['hitPolicy']
    except KeyError:
        hit_policy = 'unique'

    return hit_policy.lower()
