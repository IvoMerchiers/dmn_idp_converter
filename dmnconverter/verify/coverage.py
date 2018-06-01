import dmnconverter.tools.texttools as text_tools
from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.verify.verfication import Verification


class Coverage(Verification):

    def build_structure(self, decision_table: DecisionTable) -> [str]:
        # ModelInt
        # TODO: proper method to introduce ranges of variables
        modelint_start = 0
        modelint_stop = 30
        structure = ["ModelInt = {" + str(modelint_start) + ".." + str(modelint_stop) + "}"]

        # Variables
        structure.append(
            'Variable = {' + super().list_meta_variables(text_tools.enquote_list(decision_table.input_labels)) + '}')

        # Domain and ranges
        (input_domain, input_range) = super().specify_meta_domain(decision_table.input_label_dict, 0, 20)

        # add to structure
        structure.append('Domain = {' + '; '.join(text_tools.make_str(input_domain)) + '}')
        structure.append('Range = {' + '; '.join(text_tools.make_str(input_range)) + '}')

        #  Rule components
        structure.append('RuleIn = {' + '; '.join(
            super().build_meta_input_rule(decision_table.input_labels, decision_table.input_rule_comp)) + '}')
        return structure

    def build_vocabulary(self, decision_table: DecisionTable) -> [str]:
        vocabulary = ["type RuleNr isa int",
                      "type CaseNr isa int",
                      "type Variable",
                      "type InputVariable isa Variable",
                      "",
                      "type ModelInt isa int // Sets range of all integers in the problem",
                      "type Value contains ModelInt",
                      "",
                      "// Assigns a value to a variable",
                      "VarValue(Variable):Value",
                      "",
                      "// Needed to identify satisfied rules",
                      "Match(RuleNr,Variable)",
                      "Triggered(RuleNr)    ",
                      "CountTriggers:int",
                      "",
                      "// Domains and ranges of variables",
                      "Domain(Variable,Value)",
                      "Range(Variable,Value,Value) // inclusive range with min and max as values",
                      "",
                      "// Allow alternative comparison operators",
                      "type Operator constructed from {eq,less, leq, grt, geq}",
                      "Compare(Variable, Operator, Value)",
                      "",
                      "// RuleComp to decompose into entries.",
                      "RuleIn(RuleNr, CaseNr, InputVariable, Operator, Value)"
                      ]
        return vocabulary

    def build_theory(self, decision_table: DecisionTable) -> [str]:
        theory = ["// CORRECT UNDERSTANDING OF RULES    ",
                  "{",
                  "!rN[RuleNr],var[InputVariable]: Match(rN,var)<- ?cN[CaseNr]: ?val1[Value], op1[Operator]: RuleIn("
                  "rN,cN,var,op1, val1) & (",
                  "!val2[Value], op2[Operator]: RuleIn(rN,cN,var, op2, val2) => Compare(var,op2,val2) ).",
                  "!rN[RuleNr],var[InputVariable]: Match(rN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn("
                  "rN, cN,var, op, val).",
                  "}",
                  "",
                  "// Define when a rule is triggered",
                  "{ !rN[RuleNr]: Triggered(rN)<- !var[InputVariable]:  Match(rN,var). }",
                  "",
                  "",
                  "",
                  "// TABLE COVERAGE CHECK",
                  "CountTriggers = #{rN[RuleNr]:Triggered(rN)}=0.",
                  "",
                  "",
                  "// RESTRICT DOMAINS & RANGES",
                  "// for all good values within the range, link these to the domain",
                  "!var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue(var) =< maxVal).",
                  "",
                  "// If a domain is defined, all variable assignments match it.x",
                  "!var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue(var)=val2).",
                  "",
                  "// DEFINE COMPARISON OPERATORS",
                  "{  ",
                  "	!a[Variable], val[Value]: Compare(a, eq, val) <-  VarValue(a)=val.",
                  "	!a[Variable], val[Value]: Compare(a, less, val) <-  VarValue(a)<val.",
                  "	!a[Variable], val[Value]: Compare(a, leq, val) <-  VarValue(a)=<val.",
                  "	!a[Variable], val[Value]: Compare(a, grt, val) <-  VarValue(a)>val.",
                  "	!a[Variable], val[Value]: Compare(a, geq, val) <-  VarValue(a)>=val.",
                  "}"]
        return theory
