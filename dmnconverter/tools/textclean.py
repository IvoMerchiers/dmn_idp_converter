
def clean_text(entry) -> str:
    """removes accents and adds underscores to text"""
    text = entry[0].text
    if text is not None:
        text = text.replace('"', '')
        text = text.replace(' ', '_')
    return text

