import xml.etree.ElementTree as ET
from dmnconverter.converter import DMNConverter as Dmn

# --- values---
directory='..\DMNTables\\'
file_name = "RunningExample"

# fileName = "..\DMNTables\BepaalTypeWoningBoolean.dmn"
#outputName = 'RunningExample.idp'

# ---- Script----
file_location=directory+file_name+'.dmn'
output_name=file_name+'.idp'
conv = Dmn()
conv.read(file_location)
conv.print_inductive(output_name)
