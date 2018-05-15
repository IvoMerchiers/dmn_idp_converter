
import dmnconverter.tools.texttools as text_tools

# TODO: get functions these out of general and put these into meta representation (or build proper class hiararchy).
from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.transform.general import list_meta_variables, specify_meta_domain, build_meta_input_rule
from dmnconverter.transform.general import MetaLanguageConverter


class MetaConverter(MetaLanguageConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        # Some constants
        # TODO: proper method to introduce ranges of variables
        modelint_start = 0
        modelint_stop = 20

        dmn_table = decision_tables[0]

        # read out from structure
        input_label_dict = dmn_table.input_label_dict
        output_label_dict = dmn_table.output_label_dict
        input_rule_comp = dmn_table.input_rule_comp
        output_rule_comp = dmn_table.output_rule_comp
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels

        # Vocabulary is fixed
        vocabulary = self.build_vocabulary()

        # Theory is fixed
        theory = self.build_theory()

        # --- start building structure ---
        # ModelInt
        structure = ["ModelInt = {" + str(modelint_start) + ".." + str(modelint_stop) + "}"]

        # Variables
        structure.append('InputVariable = {' + list_meta_variables(text_tools.enquote_list(input_labels)) + '}')
        structure.append('OutputVariable = {' + list_meta_variables(text_tools.enquote_list(output_labels)) + '}')

        # Domain and ranges
        (input_domain, input_range) = specify_meta_domain(input_label_dict, 0, 20)
        (output_domain, output_range) = specify_meta_domain(output_label_dict, 0, 20)
        # merge both input and output
        domain = input_domain + output_domain
        ranges = input_range + output_range
        # add enumerated domains and ranges to structure
        structure.append('Domain = {' + '; '.join(text_tools.make_str(domain)) + '}')
        structure.append('Range = {' + '; '.join(text_tools.make_str(ranges)) + '}')

        #  Rule components
        structure.append('RuleIn = {' + '; '.join(build_meta_input_rule(input_labels, input_rule_comp)) + '}')
        structure.append('RuleOut = {' + '; '.join(self.__build_output_rule(output_labels, output_rule_comp)) + '}')

        return vocabulary, theory, structure

    @staticmethod
    def __build_output_rule(labels: list, rule_components: list) -> list:
        rule = []
        amount_entries = len(labels)
        enquoted_labels = text_tools.enquote_list(labels)

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
                        value = text_tools.enquote(value)
                    rule.append(str(rule_nr + 1) + ',' + label + ',' + value)
        return rule

    @staticmethod
    def build_vocabulary() -> [str]:
        vocabulary = [
            "type RuleNr isa int",
            "type CaseNr isa int",
            "type Variable",
            "type InputVariable isa Variable",
            "type OutputVariable isa Variable",
            "",
            "type ModelInt isa int // Sets range of all integers in the problem",
            "type Value contains ModelInt",
            "",
            "// Assigns a value to a variable",
            "VarValue(Variable):Value",
            "OutputVarValue(OutputVariable):Value",
            "",
            "// Indicate if the current assignments 'trigger' a rule",
            "Triggered(RuleNr)",
            "",
            "// Matched and trivial rule entries",
            "Match(RuleNr,Variable)",
            "", "// Domains and ranges of variables",
            "Domain(Variable,Value)",
            "Range(Variable,Value,Value) // inclusive range with min and max as values",
            "",
            "// Allow alternative comparison operators",
            "type Operator constructed from {eq,less, leq, grt, geq}",
            "Compare(Variable, Operator, Value)",
            "",
            "// RuleComp forms a component of a rule",
            "RuleIn(RuleNr, CaseNr, InputVariable, Operator, Value)",
            "RuleOut(RuleNr, OutputVariable, Value) // output can only be equal",
            ""
        ]
        return vocabulary

    @staticmethod
    def build_theory() -> [str]:
        theory = [
            "// CORRECT OUTPUT OF RULES",
            "// Define meaning of outputVariable",
            "{ !var[OutputVariable], val[Value]: OutputVarValue(var)=val <- VarValue(var)=val. }",
            "",
            "	// Match predicate",
            "{",
            "!rN[RuleNr],var[InputVariable]: Match(rN,var)<- ?cN[CaseNr]: ?val1[Value], op1[Operator]: RuleIn(rN,"
            "cN,var,op1, val1) & ( !val2[Value], op2[Operator]: RuleIn(rN,cN,var, op2, val2) => Compare(var,op2,"
            "val2) ).",
            "!rN[RuleNr],var[InputVariable]: Match(rN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn(rN, cN,"
            "var, op, val).",
            "}",
            "",
            "// Define when a rule is triggered",
            "{ !rN[RuleNr]: Triggered(rN)<- !var[InputVariable]:  Match(rN,var). }",
            "",
            "// Assign output to a triggered rule",
            "{ !yvar[OutputVariable], yval[Value]: OutputVarValue(yvar)=yval<- ?n[RuleNr]:RuleOut(n, yvar, "
            "yval) & Triggered(n). }",
            "",
            "// RESTRICT DOMAINS & RANGES",
            "// for all good values within the range, link these to the domain",
            "!var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue(var) "
            "=< maxVal).",
            "",
            "// If a domain is defined, all variable assignments match it.x",
            "!var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue(var)=val2).",
            "",
            "// DEFINE COMPARISON OPERATORS",
            "{  ",
            "    !a[Variable], val[Value]: Compare(a, eq, val) <-  VarValue(a)=val.",
            "    !a[Variable], val[Value]: Compare(a, less, val) <-  VarValue(a)<val.",
            "    !a[Variable], val[Value]: Compare(a, leq, val) <-  VarValue(a)=<val.",
            "    !a[Variable], val[Value]: Compare(a, grt, val) <-  VarValue(a)>val.",
            "    !a[Variable], val[Value]: Compare(a, geq, val) <-  VarValue(a)>=val.",
            "}"
        ]
        return theory

