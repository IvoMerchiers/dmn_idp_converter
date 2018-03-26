
def clean_text(entry):
    """Read one line of entries (1 rule) and returns these in a list"""
    text = entry[0].text
    if text is not None:
        text = text.replace('"', '')
        text = text.replace(' ', '_')
    return text

