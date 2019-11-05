# dmn_idp_converter
## Summary
Converter to translate Camunda DMN tables into IDP3 code


## Installation
### Dependencies
This package only relies on the python standard library:
* [xml](https://docs.python.org/3.5/library/xml.etree.elementtree.html#xml.etree.ElementTree.XML)
* [re](https://docs.python.org/3.5/library/re.html)

### Installing the package
```
pip install git+git://github.com/IvoMerchiers/dmn_idp_converter
```

## Supported DMN tables
Currently only DMN tables created by the [Camunda Modeller](https://camunda.com/download/modeler/) are supported.
Other XML representations of DMN tables might work if they use the official OMG standard, but this has not been tested.
Networks of DMN tables are also supported, as long as there are no name-space conflicts.

## Supported output
The package converts the DMN table into IDP3 code. Multiple transformations are possible, with distinct goals.

* **Direct translation:** Focuses on speed and human-readability. Only supports 'Unique' hit policy
  * Inductive formalism: Most performant version, using FO(.) definitions
  * Implicative formalism: More natural, using implications
  
* **Meta model:** Slower and harder to read, but higher expressiveness allows additional inferences
  * Core meta model: Model that encodes the full DMN tables for multiple hit polices 
  * Table verification: Can find inconsistencies in a single table.
  * Rule Learning: Can combine given rules and data to find a consistent DMN table.
 
Information on how to run IDP code can be found on [the official site](https://dtai.cs.kuleuven.be/software/idp).

## Contribution
Users are encouraged to help with supporting other data types, bugfixing and adding new features.
  
## Author
* **Ivo Merchiers** - *Development* - [IvoMerchiers](https://github.com/IvoMerchiers) 

## License
This project is licensed under the MIT License - see the [License](LICENSE) file for details

## Acknowledgements
* Developed for KUL as a thesis
* Assisted by Simon Marynissen
* Table verification approach inspired by [Calvanese et al.](https://arxiv.org/abs/1603.07466v1)
