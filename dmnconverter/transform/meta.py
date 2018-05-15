import itertools
from boltons.setutils import IndexedSet

import dmnconverter.tools.texttools as text_tools


# TODO: get functions these out of general and put these into meta representation (or build proper class hiararchy).
from dmnconverter.tools.decisiontable import DecisionTable
from dmnconverter.transform.general import MetaLanguageConverter


class MetaConverter(MetaLanguageConverter):
    # TODO encode this better?
    def build_structure(self, decision_table: DecisionTable) -> [str]:
        pass

    def convert(self, decision_tables: [DecisionTable]) -> ([str], [str], [str]):

        vocabulary = self.build_vocabulary()
        theory = self.build_theory()

        structure_dictionaries = [self.build_structure_dict(decision_table) for decision_table in decision_tables]
        predicate_names = structure_dictionaries[0].keys()
        # Loop over every predicate and only keep unique entries for those predicates
        structure: [str] = []
        for predicate in predicate_names:
            value_list = [structure_dictionary[predicate] for structure_dictionary in structure_dictionaries]
            flat_value_list = list(itertools.chain.from_iterable(value_list))
            # remove doubles
            unique_value_list = list(IndexedSet(flat_value_list))
            values_string = '; '.join(unique_value_list)
            structure.append(predicate + " = {" + values_string + "}")

        return vocabulary, theory, structure

    def build_structure_dict(self, dmn_table: DecisionTable) -> dict:
        """
Build a dictionary of the structure for a specific decision table
        :rtype: dict
        :param dmn_table:
        :return: dictionary with keys the name of the relevant predicate. Values are lists containing all the relevant entries.
        """
        modelint_start = 0
        modelint_stop = 20

        structure_dict = dict()

        # Model int
        structure_dict['ModelInt'] = [str(modelint_start) + ".." + str(modelint_stop)]

        # Table Name
        structure_dict['TableName'] = [dmn_table.table_name]

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
        structure_dict['RuleIn'] = text_tools.make_str(domain)
        structure_dict['RuleOut'] = text_tools.make_str(ranges)

        # Policies
        structure_dict['TablePolicy'] = [dmn_table.table_name + "," + dmn_table.hit_policy]

        #  Rule components
        input_rule_comp = dmn_table.input_rule_comp
        output_rule_comp = dmn_table.output_rule_comp
        input_labels = dmn_table.input_labels
        output_labels = dmn_table.output_labels
        # TODO: make these following functions take decision table as input
        input_rules = self.build_meta_input_rule(input_labels, input_rule_comp)
        output_rules = self.__build_output_rule(output_labels, output_rule_comp)
        structure_dict['RuleIn'] = self.add_table_name(dmn_table, input_rules)
        structure_dict['RuleOut'] = self.add_table_name(dmn_table, output_rules)

        # Priorities

        return structure_dict

    @staticmethod
    def add_table_name(dmn_table: DecisionTable, string_list: [str]) -> [str]:
        """
Adds the name of the relevant table to the start of every element in the list.
        :param dmn_table:
        :param string_list:
        """
        table_name = dmn_table.table_name
        return [table_name + "," + element for element in string_list]

    @staticmethod
    def __build_output_rule(labels: list, rule_components: list) -> [str]:
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
    # Todo: update vocabulary and adapt to number of tables!
    @staticmethod
    def build_vocabulary(**kwargs) -> [str]:
        vocabulary = ["type RuleNr isa int",
                      "type CaseNr isa int",
                      "type Variable",
                      "type InputVariable isa Variable",
                      "type OutputVariable isa Variable",
                      "",
                      "type TableName",
                      "type ModelInt isa int // Sets range of all integers in the problem",
                      "type Value contains ModelInt",
                      "// Assigns a value to a variable",
                      "VarValue(Variable):Value",
                      "OutputVarValue(OutputVariable):Value",
                      "// Indicate if the current assignments 'trigger' a rule",
                      "Triggered(TableName, RuleNr)",
                      "",
                      "// Matched and trivial rule entries",
                      "Match(TableName, RuleNr,Variable)",
                      "// Domains and ranges of variables",
                      "Domain(Variable,Value)",
                      "Range(Variable,Value,Value) // inclusive range with min and max as values",
                      "// Allow alternative comparison operators",
                      "type Operator constructed from {eq,less, leq, grt, geq}",
                      "Compare(Variable, Operator, Value)",
                      "// RuleComp forms a component of a rule",
                      "RuleIn(TableName, RuleNr, CaseNr, InputVariable, Operator, Value)",
                      "RuleOut(TableName, RuleNr, OutputVariable, Value) // output can only be equal",
                      "",
                      "type Policy constructed from {unique, first, priority}",
                      "TablePolicy(TableName):Policy",
                      "",
                      "type Priority isa int",
                      "RulePriority(TableName, RuleNr, Priority)"]
        return vocabulary

    @staticmethod
    def build_theory(**kwargs) -> [str]:
        theory = [
            "// CORRECT OUTPUT OF RULES",
            "// Define meaning of outputVariable",
            "{ !var[OutputVariable], val[Value]: OutputVarValue(var)=val <- VarValue(var)=val. }",
            "// Define match predicate",
            "{",
            "!tN[TableName], rN[RuleNr],var[InputVariable]: Match(tN, rN, var)<- ?cN[CaseNr]: ?val1[Value], "
            "op1[Operator]: RuleIn(tN,rN,cN,var,op1, val1) & ( !val2[Value], op2[Operator]: RuleIn(tN,rN,cN,var, op2, "
            "val2) => Compare(var,op2,val2) ).",
            "!rN[RuleNr],var[InputVariable]: Match(tN,rN,var) <- ?0 val[Value],cN[CaseNr], op[Operator]: RuleIn(tN,"
            "rN, cN,var, op, val).",
            "}",
            "",
            "// Define when a rule is triggered",
            "{ !tN[TableName], rN[RuleNr]: Triggered(tN,rN)<- !var[InputVariable]:  Match(tN,rN,var). }",
            "",
            "// Assign output based on hit policy of the table",
            "{ ",
            "!tN[TableName], yvar[OutputVariable], yval[Value]:  OutputVarValue(yvar)=yval<- ?n[RuleNr]: TablePolicy("
            "tN) = unique & RuleOut(tN,n, yvar, yval) & Triggered(tN,n). ",
            "!tN[TableName], yvar[OutputVariable], yval[Value]: OutputVarValue(yvar) = yval<- ?n[RuleNr]: "
            "TablePolicy(tN) = first & RuleOut(tN,n, yvar, yval) & n = min{n2[RuleNr]:Triggered(tN,n2):n2}.",
            "!tN[TableName], yvar[OutputVariable], yval[Value]: OutputVarValue(yvar) = yval<- ?n[RuleNr], "
            "maxPr[Priority]: TablePolicy(tN) = priority & RuleOut(tN,n, yvar, yval) &  Triggered(tN,"
            "n) & RulePriority(tN,n, maxPr) & maxPr = max{n2[RuleNr], pr[Priority]:Triggered(tN,n2) & RulePriority("
            "tN,n2,pr) :pr}. ",
            "}",
            "// RESTRICT DOMAINS & RANGES",
            "// for all good values within the range, link these to the domain",
            "!var[Variable], minVal[Value], maxVal[Value]: Range(var, minVal, maxVal) => (minVal =< VarValue(var) =< "
            "maxVal).",
            "// If a domain is defined, all variable assignments match it.x",
            "!var[Variable], val1[Value]: ?val2[Value]: Domain(var,val1)=> (Domain(var,val2) & VarValue(var)=val2).",
            "// DEFINE COMPARISON OPERATORS",
            "{  ",
            "   !a[Variable], val[Value]: Compare(a, eq, val) <-  VarValue(a)=val.",
            "   !a[Variable], val[Value]: Compare(a, less, val) <-  VarValue(a)<val.        ",
            "   !a[Variable], val[Value]: Compare(a, leq, val) <-  VarValue(a)=<val.",
            "   !a[Variable], val[Value]: Compare(a, grt, val) <-  VarValue(a)>val.",
            "   !a[Variable], val[Value]: Compare(a, geq, val) <-  VarValue(a)>=val.",
            "}"
        ]
        return theory



