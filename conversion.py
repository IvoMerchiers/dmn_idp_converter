
from dmnconverter.converter import DMNConverter

# --- Paths ---
directory = '..\DMNTables\\'
file_name = "chainBBQ"
file_location = directory + file_name + '.dmn'
output_name = file_name + '.idp'

# --- Convert ---
converter = DMNConverter()
converter.read(file_location)
converter.verify_all(output_name)
