
def clean_text(entry) -> str:
    """removes accents and adds underscores inside space separated strings"""
    text = entry[0].text
    if text is not None:
        text = text.replace('"', '')
        text = text.replace(' ', '_')
        text = text.replace(',_', ', ')
    return text


def make_str(old_list: list) -> [str]:
    """
Turn every element of the list into a string
    :param old_list:
    :return:
    """
    return [str(x) for x in old_list]


def enquote(string: str) -> str:
    enquoted = '"' + string + '"'
    return enquoted


def enquote_list(old_list: [str]) -> [str]:
    return [enquote(string) for string in old_list]