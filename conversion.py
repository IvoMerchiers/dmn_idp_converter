import xml.etree.ElementTree as ET
from dmnconverter.converter import DMNConverter as Dmn

# --- values---
# fileName="..\DMNTables\BepaalMaxKl.dmn"
fileName = "..\DMNTables\BepaalTypeWoningBoolean.dmn"
outputName = 'BepaalTypeWoningBoolean.idp'

# ---- Script----
conv = Dmn()
conv.read(fileName)
conv.print_implicative(outputName)
