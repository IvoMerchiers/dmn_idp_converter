import dmnconverter.tools.print as printer
import dmnconverter.transform.general


def print_file(file_name, input_rule_comp: list, input_label_dict: dict,
               output_rule_comp: list, output_label_dict: dict) -> None:
    """
    Print table as a txt file in the meta framework. This means all info about specific dec table
    is in the structure.
    :param file_name: name of output file
    :param input_rule_comp: 2d array of rule components
    :param input_label_dict: dictionary of labels and the tuple indicating their domain
    :param output_rule_comp: 2d array of output rule comps
    :param output_label_dict: dictionary of output labels and their domains
    """
    # Some constants
    # TODO: proper method to introduce ranges of variables
    modelint_start = 0
    modelint_stop = 20

    # Vocabulary is fixed
    vocabulary = ["type RuleNr isa int",
                  "type Variable",
                  "type InputVariable isa Variable",
                  "type OutputVariable isa Variable",
                  '',
                  "type ModelInt isa int // Sets range of all integers in the problem",
                  "type Value contains ModelInt",
                  '',

                  "// Assigns a value to a variable",
                  "VarValue(Variable):Value",
                  "OutputVarValue(OutputVariable):Value",
                  '',

                  "// Indicate if the current assignments 'trigger' a rule",
                  "Triggered(RuleNr)",
                  '',

                  "// Domains and ranges of variables",
                  "Domain(Variable,Value)",
                  "Range(Variable,Value,Value) // inclusive range with min and max as values",
                  '',

                  "// Allow alternative comparison operators",
                  "type Operator constructed from {eq,less, leq, grt, geq}",
                  "Compare(Variable, Operator, Value)",
                  '',

                  "// RuleComp forms a component of a rule",
                  "RuleIn(RuleNr, InputVariable, Operator, Value)",
                  "RuleOut(RuleNr, OutputVariable, Value) // output can only be equal]"]

    # Theory is fixed
    theory = ['// CORRECT OUTPUT OF RULES',
              '',
              "// Define meaning of outputVariable",
              "{ !var[OutputVariable], val[Value]: OutputVarValue(var)=val <- VarValue(var)=val. }",
              '',
              "// Define when a rule is triggered",
              "{ !rN[RuleNr]: Triggered(rN)<- !var[InputVariable], val[Value], op[Operator]: RuleIn(rN,var, op, "
              "val) => Compare(var,op,val) . }",
              '',
              "// Assign output to a triggered rule",
              "{ !yvar[OutputVariable], yval[Value]: OutputVarValue(yvar)=yval<- ?n[RuleNr]:RuleOut(n, yvar, "
              "yval) & Triggered(n). }",
              '',
              "// RESTRICT DOMAINS & RANGES",
              '',
              "// Experimenting with setting a range",
              "// for all good values within the range, link these to the domain",
              "!var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue(var) "
              "=< maxVal).",
              '',
              "// All variable assignments match their domain",
              "!var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue(var)=val2).",
              '',
              "// DEFINE COMPARISON OPERATORS",
              "{  ",
              "!a[Variable], val[Value]: Compare(a, eq, val) <-  VarValue(a)=val.",
              "!a[Variable], val[Value]: Compare(a, less, val) <-  VarValue(a)<val.",
              "!a[Variable], val[Value]: Compare(a, leq, val) <-  VarValue(a)=<val.",
              "!a[Variable], val[Value]: Compare(a, grt, val) <-  VarValue(a)>val.",
              "!a[Variable], val[Value]: Compare(a, geq, val) <-  VarValue(a)>=val.",
              "}"]

    # Find output labels
    input_labels = list(input_label_dict.keys())
    output_labels = list(output_label_dict.keys())

    # --- start building structure ---
    # ModelInt
    structure = ["ModelInt = {" + str(modelint_start) + ".." + str(modelint_stop) + "}"]

    # Variables
    structure.append('InputVariable = {' + __list_variables(__enquote_list(input_labels)) + '}')
    structure.append('OutputVariable = {' + __list_variables(__enquote_list(output_labels)) + '}')

    # Domain and ranges
    (input_domain, input_range) = __specify_domain(input_label_dict, 0, 20)
    (output_domain, output_range) = __specify_domain(output_label_dict, 0, 20)
    # merge both input and output
    domain = input_domain + output_domain
    ranges = input_range + output_range
    # add to structure
    structure.append('Domain = {' + '; '.join(__make_str(domain)) + '}')
    structure.append('Range = {' + '; '.join(__make_str(ranges)) + '}')

    #  Rule components
    structure.append('RuleIn = {' + '; '.join(__build_input_rule(input_labels, input_rule_comp)) + '}')
    structure.append('RuleOut = {' + '; '.join(__build_output_rule(output_labels, output_rule_comp)) + '}')

    printer.print_idp(file_name, vocabulary, theory, structure)


def __list_variables(labels: list) -> str:
    listing = '; '.join(labels)
    return listing


def __specify_domain(label_dict: dict, range_start: int, range_stop: int) -> tuple:
    """
Determine domain and range of variables in the dictionary
    :param label_dict:
    :return: tuple of all Domain and Ranges that are associated to this dictionary (list(str),list(str))
    """
    domain = []
    ranges = []

    keys = label_dict.keys()
    for key in keys:
        current_variable = __enquote(str(key))
        (type_ref, values) = label_dict[key]

        if type_ref in ['string', 'boolean']:
            value_list = values.split(',')
            domain.extend([current_variable + ',' + value for value in __enquote_list(value_list)])
        elif type_ref in ['integer']:
            ranges.append(current_variable + ',' + str(range_start) + ',' + str(range_stop))
        else:
            raise TypeError('Unknown type ' + str('type_ref'))
    return domain, ranges


def __build_input_rule(labels: list, rule_components: list) -> list:
    """
Make list of all rule components, ready to be entered in the IDP structure (with ";" separation between elements)
    :param labels:
    :param rule_components:
    :return:
    """
    rule = []
    amount_entries = len(labels)
    enquoted_labels = __enquote_list(labels)

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
        comparator_name = dmnconverter.transform.general.encode_comparison(comparator)
        # enquote non integer values
        try:
            int(value)
        except ValueError:
            value = __enquote(value)
        entry = [str(rule_nr) + ',' + label + ',' + comparator_name + ',' + value]
    return entry


def __build_output_rule(labels: list, rule_components: list) -> list:
    rule = []
    amount_entries = len(labels)
    enquoted_labels = __enquote_list(labels)

    for rule_nr in range(len(rule_components)):
        rule_component = rule_components[rule_nr]
        for entry_nr in range(amount_entries):
            entry = rule_component[entry_nr]
            if entry is not None:
                label = enquoted_labels[entry_nr]
                (comparator, value) = entry
                # enquote non integer values
                try:
                    int(value)
                except ValueError:
                    value = __enquote(value)
                rule.append(str(rule_nr + 1) + ',' + label + ',' + value)
    return rule


def __make_str(old_list: list) -> list:
    """
Turn every element of the list into a string
    :param old_list:
    :return:
    """
    return [str(x) for x in old_list]


def __enquote(string: str) -> str:
    enquoted = '"' + string + '"'
    return enquoted


def __enquote_list(old_list: list) -> list:
    return [__enquote(string) for string in old_list]
