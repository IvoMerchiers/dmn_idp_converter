""""
Uses meta model with multiple assignments to learn a single table. Can be used by itself, or combined with a (partial) table
"""
import warnings

from boltons.setutils import IndexedSet

from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.verify.verification import Verification


class TableLearner(Verification):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        if len(decision_tables) > 1:
            warnings.warn("Only first table is verified even though multiple DMN tables were given")
        dmn_table: DecisionTable = decision_tables[0]

        vocabulary = self.build_vocabulary(dmn_table)
        theory = self.build_theory(dmn_table)
        structure = self.build_structure(dmn_table)

        return vocabulary, theory, structure

    def build_structure(self, decision_table: DecisionTable):
        structure_dict = super().build_structure_dict(decision_table)
        predicate_names = structure_dict.keys()
        structure: [str] = []
        for predicate in predicate_names:
            value_list = structure_dict[predicate]
            # remove doubles
            unique_value_list = list(IndexedSet(value_list))
            values_string = '; '.join(unique_value_list)
            structure.append(predicate + "<ct> = {" + values_string + "}")
        return structure

    def build_vocabulary(self, decision_table: DecisionTable) -> [str]:
        vocabulary = ["type RuleNr isa int",
                      "type CaseNr isa int",
                      "type AssignNr isa int",
                      "type Variable",
                      "type InputVariable isa Variable",
                      "type OutputVariable isa Variable",
                      "",
                      "type ModelInt isa int // Sets range of all integers in the problem",
                      "type Value contains ModelInt",
                      "",
                      "// Assigns a value to a variable",
                      "VarValue(AssignNr, Variable):Value",
                      "OutputVarValue(AssignNr, OutputVariable):Value",
                      "",
                      "// Domains and ranges of variables",
                      "Domain(Variable,Value)",
                      "Range(Variable,Value,Value) // inclusive range with min and max as values",
                      "",
                      "// Matched and trivial rule entries",
                      "Match(RuleNr, AssignNr, Variable)",
                      "// Indicate if the current assignments 'trigger' a rule",
                      "Triggered(RuleNr, AssignNr)",
                      "",
                      "// Allow alternative comparison operators",
                      "type Operator constructed from {eq,less, leq, grt, geq} // only equality here for simplification",
                      "Compare(AssignNr, Variable, Operator, Value)",
                      "",
                      "// Rule components encode rule entries",
                      "RuleIn(RuleNr, CaseNr, InputVariable, Operator, Value)",
                      "RuleOut(RuleNr, OutputVariable, Value)",
                      "",
                      "type Policy constructed from {unique, first, priority}",
                      "TablePolicy():Policy",
                      "",
                      "type Priority isa int",
                      "RulePriority(RuleNr, Priority)",
                      "",
                      "// Constant to store number of used rules",
                      "UsedRules:int"]
        return vocabulary

    def build_theory(self, decision_table: DecisionTable) -> [str]:
        theory = ["// Count number of 'used' rules",
                  "UsedRules=#{n[RuleNr]:?var[Variable], val[Value]: RuleOut(n,var,val) | (?cN[CaseNr]: RuleIn(n,cN,var,eq,val))}.",
                  "",
                  "// CORRECT OUTPUT OF RULES",
                  "// Define meaning of outputVariable",
                  "{ !aN[AssignNr], var[OutputVariable], val[Value]: OutputVarValue(aN,var)=val <- VarValue(aN,var)=val. }",
                  "",
                  "// Match predicate",
                  "{",
                  "	!rN[RuleNr], aN[AssignNr], var[InputVariable]: Match(rN,aN,var)<- ?cN[CaseNr]: ?val1[Value], op1[Operator]:",
                  "RuleIn(rN,cN,var,op1, val1) & ( !val2[Value], op2[Operator]: RuleIn(rN,cN,var, op2, val2) => Compare(aN,var,op2,val2) ).",
                  "	!rN[RuleNr], aN[AssignNr], var[InputVariable]: Match(rN,aN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn(rN, cN,var,",
                  "op, val).",
                  "}",
                  "",
                  "// Define when a rule is triggered",
                  "{ !rN[RuleNr], aN[AssignNr]: Triggered(rN,aN)<- !var[InputVariable]:  Match(rN,aN,var). }",
                  "",
                  "// Assign output based on hit policy of the table",
                  "{ ",
                  "	!aN[AssignNr], yvar[OutputVariable], yval[Value]:  OutputVarValue(aN,yvar)=yval <- ?n[RuleNr]: TablePolicy() = unique &",
                  "RuleOut(n, yvar, yval) & Triggered(n,aN). ",
                  "	!aN[AssignNr], yvar[OutputVariable], yval[Value]: OutputVarValue(aN,yvar)=yval<- ?n[RuleNr]: TablePolicy() = first &",
                  "RuleOut(n, yvar, yval) & n = min{n2[RuleNr]:Triggered(n2,aN):n2}.",
                  "	!aN[AssignNr], yvar[OutputVariable], yval[Value]: OutputVarValue(aN,yvar)=yval<- ?n[RuleNr], maxPr[Priority]: TablePolicy() =",
                  "priority & RuleOut(n, yvar, yval) &  Triggered(n,aN) & RulePriority(n, maxPr) & maxPr = max{n2[RuleNr],",
                  "pr[Priority]:Triggered(n2,aN) & RulePriority(n2,pr) :pr}. ",
                  "}",
                  "",
                  "// RESTRICT DOMAINS & RANGES",
                  "// for all good values within the range, link these to the domain",
                  "!aN[AssignNr], var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue(aN,var) =< maxVal).",
                  "",
                  "// If a domain is defined, all variable assignments match it.x",
                  "!aN[AssignNr], var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue(aN,var)=val2).",
                  "",
                  "// DEFINE COMPARISON OPERATORS",
                  "{  ",
                  "	!aN[AssignNr],a[Variable], val[Value]: Compare(aN,a, eq, val) <-  VarValue(aN,a)=val.",
                  "	!aN[AssignNr],a[Variable], val[Value], compVal[Value]: Compare(aN,a, less, compVal) <-  VarValue(aN,a)=val &",
                  "val<compVal.        ",
                  "	!aN[AssignNr],a[Variable], val[Value], compVal[Value]: Compare(aN,a, leq, compVal) <-  VarValue(aN,a)=val & val=<compVal.",
                  "	!aN[AssignNr],a[Variable], val[Value], compVal[Value]: Compare(aN,a, grt, compVal) <-  VarValue(aN,a)=val & val>compVal.",
                  "	!aN[AssignNr],a[Variable], val[Value], compVal[Value]: Compare(aN,a, geq, compVal) <-  VarValue(aN,a)=val & val>=compVal.",
                  "}",
                  "",
                  "// VERIFY PROPERTIES OF RULE COMPONENTS",
                  "// All values in rule components should be either in domain or in range of that variable",
                  "!rN[RuleNr], cN[CaseNr], var[Variable], op[Operator], val[Value], minVal[Value], maxVal[Value]: (Range(var, minVal, "
                  "maxVal) &", "RuleIn(rN, cN, var, op, val)) => (minVal =< val =< maxVal)."]
        return theory
