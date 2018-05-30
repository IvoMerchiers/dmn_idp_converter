# dmn_idp_converter
## Summary
Converter to translate DMN tables into IDP3 code
DMN tables as defined by the OMG standard.
IDP3 as developped by the KuL DTAI group.

## Supported DMN tables
Currently only DMN tables created by the [Camunda Modeller](https://camunda.com/download/modeler/) are supported.
Networks of DMN tables are also supported, as long as there are no name-space conflicts.

## Supported output
The package converts the DMN table into IDP code. Multiple transformations are possible, with distinct goals.

* **Direct translation:** Focusses on speed and human-readability. Only supports 'Unique' hit policy
  * Inductive formalism: Most performant version, using FO(.) definitions
  * Implicative formalism: More natural, using implications
  
* **Meta model:** Slower and harder to read, but higher expressiveness allows additional inferences
  * Core meta model: Model that encodes the full DMN tables for multiple hit polices 
  * Table verification: Can find inconsistencies in single table.
  * Rule Learning: Can combine given rules and data to find a consistent DMN table.