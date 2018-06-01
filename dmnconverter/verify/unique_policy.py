""""
Unique Policy class is used to print a file to verify dmn tables using unique hit policy.
Unique hit policy has features that allow for more efficient and lightweight verification

"""

from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.verify.coverage import Coverage


class VerifyUniquePolicy(Coverage):
    """"
    Is essentially the same as coverage detection, with one line changed in the theory
    """

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
                  "CountTriggers = #{rN[RuleNr]:Triggered(rN)}~=1.",  # changed line
                  "",
                  "",
                  "// RESTRICT DOMAINS & RANGES",
                  "// for all good values within the range, link these to the domain",
                  "!var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue("
                  "var) =< maxVal).",
                  "",
                  "// If a domain is defined, all variable assignments match it.x",
                  "!var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue("
                  "var)=val2).",
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
