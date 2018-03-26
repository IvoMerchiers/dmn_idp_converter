"""
Converter for DMN code into IDP logic

Program turns a DMN table (XML table in essence) into a txt file with IDP code.
"""

import xml.etree.ElementTree as ET

class DMNConverter:
    #define used ontology
    ont='{http://www.omg.org/spec/DMN/20151101/dmn.xsd}'

    def __init__(self):
        return

    def read(self, fileName):
        """Read DMN table, extract labels and rules"""
        try:
            #Read and parse tree
            tree=ET.parse(fileName)
            root=tree.getroot()
            tableName=root.find(self.ont+'decision').attrib['name']
            decTable=root.find(self.ont+'decision').find(self.ont+'decisionTable')
            #self.decTable=decTable

            self.inputLabelDict=self.__readExpressions(decTable, 'input')
            self.outputLabelDict=self.__readExpressions(decTable, 'output')
            self.inputLabels=list(self.inputLabelDict.keys()) #use these?
            self.outputLabels=list(self.outputLabelDict.keys())
            rules=self.__readRules(decTable)
            self.inputRuleComp=rules[0]
            self.outputRuleComp=rules[1]
            self.TableRead=True

        except Exception as e:
            raise

    def printInductive(self, fileName):
        #Translat vocabulary
        vocabulary=["//Input entries with labels"]
        vocabulary.extend(self.__expressions2voc(self.inputLabelDict))
        vocabulary.append('//Output entries')
        vocabulary.extend(self.__expressions2voc(self.outputLabelDict))
        #Translate theory
        theory=self.__rules2theory('inductive')
        #print results
        self.__printIDP(fileName, vocabulary, theory)

    def printImplicative(self, fileName):
        vocabulary=["//Input entries with labels"]
        vocabulary.extend(self.__expressions2voc(self.inputLabelDict))
        vocabulary.append('//Output entries')
        vocabulary.extend(self.__expressions2voc(self.outputLabelDict))

        #Translate theory
        theory=self.__rules2theory('implicative')
        #print results
        self.__printIDP(fileName, vocabulary, theory)

    def __cleanText(self, entry):
        """Read one line of entries (1 rule) and returns these in a list"""
        text=entry[0].text
        if text is not None:
            text=text.replace('"','')
            text=text.replace(' ','_')
        return text

    def __readExpressions(self, decTable,category ):
        """Category can be 'input' or 'output'"""
        labeslDict=dict()
        for expression in decTable.findall(self.ont+category):
            label=expression.attrib['label']
            label=label.replace(' ','_')
            values=self.__readValues(category,expression)

            labeslDict[label]=values
        return labeslDict

    def __readValues(self, category, expression):
        """Returns tuple of 'typeRef' and 'values'"""
        #Find type
        if category=='input':
            typeRef=expression.find(self.ont+category+'Expression').attrib['typeRef']
        elif category=='output':
            typeRef=expression.attrib['typeRef']
        else:
            raise ValueError('Input category ' +str(category) +' not recognized')

        #Act accordingly
        if typeRef=='string':
            values=self.__cleanText(expression.find(self.ont+category+'Values'))
        elif typeRef=='boolean':
            values='true,false'
        elif typeRef=='integer':
            values='int'
        else:
            raise ValueError('Type ' +typeRef+' not yet implemented or not recognized.')
        return (typeRef,values)


    def __readRules(self,decTable):
        """Rules stored as tuple of 2 2D Matrix of entries. First matrix is input, second is output """
        #Find list of rules
        DMNrules=decTable.findall(self.ont+'rule')
        # Read input and output entries of all the rules. While doing string cleanup
        inputRuleComp=[[self.__cleanText(entry) for entry in rule.findall(self.ont+'inputEntry')] for rule in DMNrules]
        outputRuleComp=[[self.__cleanText(entry) for entry in rule.findall(self.ont+'outputEntry')] for rule in DMNrules]
        return (inputRuleComp,outputRuleComp)

    def __expressions2voc(self,labelsDict):
        """Turns a dictionary of labels into a part of a IDP vocabulary and adds it to current vocabulary"""
        vocLines=[self.__singleExpression2voc(key,labelsDict[key]) for key in labelsDict.keys()]
        return vocLines

    def __singleExpression2voc(self, label, valueTuple):
        typeRef=valueTuple[0]
        values=valueTuple[1]
        if typeRef in ['string','boolean']:
            vocLine='type '+ label +' constructed from{'+values+'}'
        elif typeRef in ['integer']:
            vocLine='type '+ label +' isa int'
        else:
            raise TypeError("type "+ typeRef + ' unknown')
        return vocLine

    def __rules2theory(self, approach):
        """returns list of string lines representing all the rules in the theory"""
        theoryLines=[]
        for i in range(len(self.inputRuleComp)): #loop over all rules
            theoryLines.append(self.__singleRule2theory(approach, self.inputLabels, self.inputRuleComp[i], self.outputLabels, self.outputRuleComp[i]))
        return theoryLines

    def __singleRule2theory(self,approach,inputLabels, inputRuleEntries, outputLabels, outputRuleEntries):
        if approach=='inductive':
            ruleString=self.__translateInductive(inputLabels, inputRuleEntries, outputLabels, outputRuleEntries)
        elif approach=='implicative':
            ruleString=self.__translateImplicative(inputLabels, inputRuleEntries, outputLabels, outputRuleEntries)
        return ''.join(ruleString)

    def __translateInductive(self,inputLabels, inputRuleEntries, outputLabels, outputRuleEntries):
        ruleString=[]
        #Cover outputs
        for i in range(len(outputRuleEntries)):
            # check only one output value
            if i > 0:
                raise ValueError('Inductive definition model can currently only have one output entry.')
            #Read specific rule
            ruleEntry=outputRuleEntries[i]
            if ruleEntry is not None:
                ruleString.append(outputLabels[i]+"="+ruleEntry)
        ruleString.append(" <- ")
        #Cover input
        for i in range(len(inputRuleEntries)):
            ruleEntry=inputRuleEntries[i]
            if ruleEntry is not None:
                ruleString.append(inputLabels[i]+"="+ruleEntry)
                ruleString.append(" & ")
        del ruleString[-1] # Remove last &
        return ''.join(ruleString)

    def __translateImplicative(self,inputLabels,inputRuleEntries,outputLabels, outputRuleEntries):
        ruleString=[]
        #Cover input
        for i in range(len(inputRuleEntries)):
            ruleEntry=inputRuleEntries[i]
            if ruleEntry is not None:
                ruleString.append(inputLabels[i]+"="+ruleEntry)
                ruleString.append(" & ")
        del ruleString[-1] #remove last &
        ruleString.append(" => ")
        for i in range(len(outputRuleEntries)):
            #Read specific rule
            ruleEntry=outputRuleEntries[i]
            if ruleEntry is not None:
                ruleString.append(outputLabels[i]+"="+ruleEntry)
                ruleString.append(" & ")
        del ruleString[-1]
        return ''.join(ruleString)


    def __printIDP(self, fileName, vocabularyStrings, theoryStrings):
        """Takes all contents of vocab and theory as list of strings and prints it as IDP code in fileName"""
        #start with vocab
        lines=['vocabulary V{']
        lines.extend(vocabularyStrings)
        #end vocab and start theory
        lines.extend(['}','\n','Theory T:V {', '//DMN table rules below:'])
        lines.extend(theoryStrings)
        lines.append('}')
        #Structure
        lines.extend(['\n', 'structure S:V{', ' // INSERT INPUT HERE', '}'])
        #main
        lines.extend(['\n', 'procedure main(){', 'stdoptions.nbmodels=200', 'printmodels(modelexpand(T,S))','}'])
        with open(fileName, 'w') as text_file:
            print('\n'.join(lines), file=text_file)
