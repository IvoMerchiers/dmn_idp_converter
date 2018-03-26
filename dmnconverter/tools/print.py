def print_idp(file_name: str, vocabulary_strings: list, theory_strings: list):
    """Takes all contents of vocab and theory as list of strings and prints it as IDP code in file_name"""
    # start with vocab
    lines = ['vocabulary V{']
    lines.extend(__indent(vocabulary_strings))
    # end vocab and start theory
    lines.extend(['}', '\n', 'Theory T:V {', '\t//DMN table rules below:'])
    lines.extend(__indent(theory_strings))
    lines.append('}')
    # Structure
    lines.extend(['\n', 'structure S:V{', '\t// INSERT INPUT HERE', '}'])
    # main
    # lines.extend(['\n', 'procedure main(){', 'stdoptions.nbmodels=200', 'printmodels(modelexpand(T,S))', '}'])
    with open(file_name, 'w') as text_file:
        print('\n'.join(lines), file=text_file)


def __indent(text: list):
    indented = ['\t' + line for line in text]
    return indented
