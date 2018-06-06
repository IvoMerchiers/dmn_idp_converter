class DecisionTable:
    """"
Structure to store information about a decision table
    :param input_rule_comp: 2d array of rule components
    :param input_label_dict: dictionary of labels and the tuple indicating their domain
    :param output_rule_comp: 2d array of output rule comps
    :param output_label_dict: dictionary of output labels and their domains
    """

    def __init__(self, ontology: str = "", table_name: str = "", hit_policy: str = "", input_label_dict: dict = dict(),
                 output_label_dict: dict = dict(),
                 input_rule_comp: [str, str] = [[""], [""]], output_rule_comp: [str, str] = [[""], [""]]):
        self.ontology = ontology
        self.table_name = table_name
        self.hit_policy = hit_policy
        self.input_label_dict = input_label_dict
        self.output_label_dict = output_label_dict
        self.input_rule_comp = input_rule_comp
        self.output_rule_comp = output_rule_comp
        self.input_labels = list(input_label_dict.keys())
        self.output_labels = list(output_label_dict.keys())
