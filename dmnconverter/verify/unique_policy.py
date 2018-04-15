import dmnconverter.tools.print as printer
import dmnconverter.transform.general as general
import dmnconverter.tools.texttools as text_tools

def print_file(file_name, input_rule_comp: list, input_label_dict: dict) -> None:

    # Some constants
    # TODO: proper method to introduce ranges of variables
    modelint_start = 0
    modelint_stop = 20

    # Vocabulary is fixed
    vocabulary = ["type RuleNr isa int",
                  "type Variable",
                  '',
                  "type ModelInt isa int // Sets range of all integers in the problem",
                  "type Value contains ModelInt",
                  '',

                  "// Assigns a value to a variable",
                  "VarValue(Variable):Value",
                  '',

                  "// Indicate if the current assignments 'trigger' a rule",
                  "Triggered(RuleNr)",
                  "CountTriggers:int",
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
                  "RuleIn(RuleNr, Variable, Operator, Value)"]

    # Theory is fixed
    theory = ['// DEFINE AND COUNT TRIGGERED RULES',
              '',
              "// Define when a rule is triggered",
              "{ !rN[RuleNr]: Triggered(rN)<- !var[Variable], val[Value], op[Operator]: RuleIn(rN,var, op, "
              "val) => Compare(var,op,val) . }",
              '',
              "CountTriggers = #{rN[RuleNr]:Triggered(rN)}~=1. // unique hit policy",
              ""
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

    # --- start building structure ---
    # Find output labels
    input_labels = list(input_label_dict.keys())

    # ModelInt
    structure = ["ModelInt = {" + str(modelint_start) + ".." + str(modelint_stop) + "}"]

    # Variables
    structure.append('Variable = {' + general.list_meta_variables(text_tools.enquote_list(input_labels)) + '}')

    # Domain and ranges
    (input_domain, input_range) = general.specify_meta_domain(input_label_dict, 0, 20)

    # add to structure
    structure.append('Domain = {' + '; '.join(text_tools.make_str(input_domain)) + '}')
    structure.append('Range = {' + '; '.join(text_tools.make_str(input_range)) + '}')

    #  Rule components
    structure.append('RuleIn = {' + '; '.join(general.build_meta_input_rule(input_labels, input_rule_comp)) + '}')

    # --- print result ---
    printer.print_idp(file_name, vocabulary, theory, structure)