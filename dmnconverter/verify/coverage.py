from dmnconverter.transform.general import MetaLanguageConverter
import dmnconverter.tools.print as printer
import dmnconverter.transform.general as general
import dmnconverter.tools.texttools as text_tools
from dmnconverter.tools.decisiontable import DecisionTable


class Coverage(MetaLanguageConverter):
    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):
        pass

    def build_structure(self, decision_table: DecisionTable) -> [str]:
        pass

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
                      "// Needed to identfiy satisfied rules",
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
                  "	!rN[RuleNr],var[InputVariable]: Match(rN,var)<- ?cN[CaseNr]: ?val1[Value], op1[Operator]: RuleIn(rN,cN,var,op1, val1) & (",
                  "!val2[Value], op2[Operator]: RuleIn(rN,cN,var, op2, val2) => Compare(var,op2,val2) ).",
                  "   !rN[RuleNr],var[InputVariable]: Match(rN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn(rN, cN,var, op, val).",
                  "}",
                  "",
                  "// Define when a rule is triggered",
                  "{ !rN[RuleNr]: Triggered(rN)<- !var[InputVariable]:  Match(rN,var). }",
                  "",
                  "",
                  "",
                  "// TABLE VERIFICATION",
                  "CountTriggers = #{rN[RuleNr]:Triggered(rN)}~=1.",
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


