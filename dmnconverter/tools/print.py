def print_idp(file_name: str, vocabulary_strings: list, theory_strings: list, structure_strings: list) -> None:
    """Takes all contents of vocab and theory as list of strings and prints it as IDP code in file_name
    :param file_name: Name of output file
    :param vocabulary_strings: list of strings, with every string denoting one line in the vocabulary
    :param theory_strings: list of strings, with every string denoting one line in the theory
    :param structure_strings: list of strings, with every string denoting one line in the structure
    """
    # Header
    # TODO: make header for transformed files
    # start with vocab
    lines = ['vocabulary V{']
    lines.extend(__indent(vocabulary_strings))
    # end vocab and start theory
    lines.extend(['}', '\n', 'theory T:V {'])
    lines.extend(__indent(theory_strings))
    lines.append('}')
    # Structure
    lines.extend(['\n', 'structure S:V{'])
    lines.extend(__indent(structure_strings))
    lines.extend(['', '\t // INSERT INPUT HERE', '}'])
    # main
    lines.extend(['\n', 'procedure main(){', 'stdoptions.nbmodels=200', 'printmodels(modelexpand(T,S))', '}'])
    with open(file_name, 'w') as text_file:
        print('\n'.join(lines), file=text_file)


def __indent(text: list) -> list:
    """
Adds 1-tab indentation to a list of strings
    :param text:
    :return:
    """
    indented = ['\t' + line for line in text]
    return indented
