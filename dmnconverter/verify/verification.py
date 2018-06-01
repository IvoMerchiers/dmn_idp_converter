""""
Does full table verification for the single hit policies
"""

import warnings

from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.transform.meta_language import MetaLanguageConverter
from dmnconverter.tools import texttools as text_tools
# from dmnconverter.verify.unique_policy import VerifyUniquePolicy


class Verification(MetaLanguageConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        if len(decision_tables) > 1:
            warnings.warn("Only first table is verified even though multiple DMN tables were given")
        dmn_table: DecisionTable = decision_tables[0]

        # todo : automatically go to single hit policy if needed
        # if dmn_table.hit_policy == 'Unique':
        #     return VerifyUniquePolicy().convert(decision_tables)

        vocabulary: [str] = self.build_vocabulary(dmn_table)
        theory = self.build_theory(dmn_table)
        structure = self.build_structure(dmn_table)
        return vocabulary, theory, structure

    def build_structure_dict(self, dmn_table: DecisionTable) -> [str]:
        """
Build structure dictionary for general verification of a single table
        :param dmn_table:
        :return:
        """
        # todo: good method for this
        modelint_start = 0
        modelint_stop = 20

        structure_dict = dict()

        # Model int
        structure_dict['ModelInt'] = [str(modelint_start) + ".." + str(modelint_stop)]

        # Variables
        (input_variables, output_variables) = self.structure_variables(dmn_table)
        structure_dict['InputVariable '] = input_variables
        structure_dict['OutputVariable '] = output_variables

        # Domain and ranges
        input_label_dict = dmn_table.input_label_dict
        output_label_dict = dmn_table.output_label_dict

        (input_domain, input_range) = self.specify_meta_domain(input_label_dict, modelint_start, modelint_stop)
        (output_domain, output_range) = self.specify_meta_domain(output_label_dict, modelint_start, modelint_stop)

        domain = input_domain + output_domain
        ranges = input_range + output_range
        # add enumerated domains and ranges to structure
        structure_dict['Domain'] = text_tools.make_str(domain)
        structure_dict['Range'] = text_tools.make_str(ranges)

        # Policies
        # fixme: currently still brackets around this when building structure
        structure_dict['TablePolicy'] = [dmn_table.hit_policy]

        #  Rule components
        structure_dict['RuleIn'] = super().build_meta_input_rule(dmn_table)
        structure_dict['RuleOut'] = super().build_output_rule(dmn_table)

        # Priorities
        # fixme support priorities
        return structure_dict

    def build_vocabulary(self, decision_table: DecisionTable) -> [str]:
        vocabulary = ["type RuleNr isa int",
                      "type CaseNr isa int",
                      "type Variable",
                      "type InputVariable isa Variable",
                      "type OutputVariable isa Variable",
                      "",
                      "type ModelInt isa int // Sets range of all integers in the problem",
                      "type Value contains ModelInt",
                      "// Assigns a value to a variable",
                      "InputVarValue(InputVariable):Value",
                      "OutputVarValue(OutputVariable,Value)",
                      "",
                      "// Indicate if the current assignments 'trigger' a rule",
                      "Match(RuleNr,Variable)",
                      "Triggered(RuleNr)",
                      "",
                      "// Domains and ranges of variables",
                      "Domain(Variable,Value)",
                      "Range(Variable,Value,Value) // inclusive range with min and max as values",
                      "// Allow alternative comparison operators",
                      "type Operator constructed from {eq,less, leq, grt, geq}",
                      "Compare(Variable, Operator, Value)",
                      "// RuleComp forms a component of a rule",
                      "RuleIn(RuleNr, CaseNr, InputVariable, Operator, Value)",
                      "RuleOut(RuleNr, OutputVariable, Value) // output can only be equal",
                      "",
                      "type Policy constructed from {unique, first, priority}",
                      "TablePolicy():Policy",
                      "",
                      "type Priority isa int",
                      "RulePriority(RuleNr, Priority)"]
        return vocabulary

    def build_theory(self, decision_table: DecisionTable) -> [str]:
        theory = ["// FIND CONFLICTING OR NON-COVERED RULES",
                  "?var[OutputVariable]: (?>1 val[Value]:OutputVarValue(var,val)) | (?0 val[Value]:OutputVarValue(var,val)).",
                  "",
                  "// CORRECT OUTPUT OF RULES",
                  "{",
                  "!rN[RuleNr],var[InputVariable]: Match( rN, var)<- ?cN[CaseNr]: ?val1[Value], op1[Operator]: RuleIn(rN,cN,var,op1, val1) & ( !val2[Value], op2[Operator]: RuleIn(rN,cN,var, op2, val2) => Compare(var,op2,val2) ).",
                  "!rN[RuleNr],var[InputVariable]: Match(rN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn(rN, cN,var, op, val).",
                  "}",
                  "",
                  "// Define when a rule is triggered",
                  "{ !rN[RuleNr]: Triggered(rN)<- !var[InputVariable]:  Match(rN,var). }",
                  "",
                  "// Assign output based on hit policy of the table",
                  "{ ",
                  "!yvar[OutputVariable], yval[Value]:  OutputVarValue(yvar,yval)<- ?n[RuleNr]: TablePolicy() = unique & RuleOut(n, yvar, yval) & Triggered(n).",
                  "!yvar[OutputVariable], yval[Value]: OutputVarValue(yvar,yval)<- ?n[RuleNr]: TablePolicy() = first & RuleOut(n, yvar, yval) & n = min{n2[RuleNr]:Triggered(n2):n2}.",
                  "!yvar[OutputVariable], yval[Value]: OutputVarValue(yvar,yval)<- ?n[RuleNr], maxPr[Priority]: TablePolicy() = priority & RuleOut(n, yvar, yval) &  Triggered(n) & RulePriority(n, maxPr) & maxPr = max{n2[RuleNr], pr[Priority]:Triggered(n2) & RulePriority(n2,pr) :pr}. ",
                  "}",
                  "",
                  "// RESTRICT DOMAINS & RANGES",
                  "// for all good values within the range, link these to the domain",
                  "!var[InputVariable], minVal[Value], maxVal[Value]: ?val[Value]: Range(var, minVal, maxVal) => (InputVarValue(var)=val & minVal =< val =< maxVal).",
                  "// If a domain is defined, all variable assignments match it.x",
                  "!var[InputVariable], val1[Value]: ?val2[Value], val3[Value]: Domain(var,val1)=> (Domain(var,val2) & InputVarValue(var)=val3 & val3=val2).",
                  "",
                  "// DEFINE COMPARISON OPERATORS",
                  "{  ",
                  "   !a[Variable], val[Value]: Compare(a, eq, val) <-  InputVarValue(a)=val.",
                  "   !a[Variable], val[Value], compVal[Value]: Compare(a, less, compVal) <-  InputVarValue(a)=val & val<compVal.        ",
                  "   !a[Variable], val[Value], compVal[Value]: Compare(a, leq, compVal) <-  InputVarValue(a)=val & val=<compVal.",
                  "   !a[Variable], val[Value], compVal[Value]: Compare(a, grt, compVal) <-  InputVarValue(a)=val & val>compVal.",
                  "   !a[Variable], val[Value], compVal[Value]: Compare(a, geq, compVal) <-  InputVarValue(a)=val & val>=compVal.",
                  "}"]
        return theory
