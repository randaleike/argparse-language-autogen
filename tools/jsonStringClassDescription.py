"""@package autogenlang
Utility to automatically generate language strings using google translate api
for the argparse libraries
"""

#==========================================================================
# Copyright (c) 2025 Randal Eike
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of self software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and self permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#==========================================================================

import re
import json

from pathgen import FileNameGenerator
from file_tools.common.param_return_tools import ParamRetDict
from file_tools.string_name_generator import StringClassNameGen
from jsonLanguageDescriptionList import LanguageDescriptionList

class StringClassDescription(object):
    """!
    String object class definitions
    """

    def __init__(self, stringDefFileName = None):
        """!
        @brief StringClassDescription constructor

        @param langListFileName (string) - Name of the json file containing
                                           the language description data
        """
        if stringDefFileName is None:
            self.filename = FileNameGenerator.getStringClassDescriptionFileName()
        else:
            self.filename = stringDefFileName
        try:
            langJsonFile = open(self.filename, 'r', encoding='utf-8')
        except FileNotFoundError:
            self.stringJasonData = {'propertyMethods':{}, 'translateMethods':{}}
        else:
            self.stringJasonData = json.load(langJsonFile)
            langJsonFile.close()

        self.transClient = None  # open it only if and when we need it

    def _definePropertyFunctionEntry(self, propertyName = "", briefDesc = "", retType = "", retDesc = "", isList = False):
        """!
        @brief Define a property string return function dictionary and
               return the entry to the caller

        @param propertyName {string} Name of the property
        @param briefDesc {string} Brief description of the function used in
                                  doxygen comment block generation
        @param retType {string} Return type string
        @param retDesc {string} Description of the return parserstr value
        @param islist {boolean} True = data is a list, False = single value

        @return {'name':<string>, 'briefDesc':<string>, 'params':[],
                 'return':ParamRetDict.buildReturnDict(retType, retDesc, isList),
                 'inline':<string>} property function dictionary
        """
        functionDict = {'name': propertyName,
                        'briefDesc': briefDesc,
                        'params': [],
                        'return': ParamRetDict.buildReturnDict(retType, retDesc, isList)
                        }
        return functionDict

    def getIsoPropertyMethodName(self):
        propertyMethodList = self.getPropertyMethodList()
        for methodName in propertyMethodList:
            if self.stringJasonData['propertyMethods'][methodName]['name'] == 'isoCode':
                return methodName

        return LanguageDescriptionList.getLanguageIsoPropertyMethodName()

    def getPropertyMethodList(self):
        """!
        @brief Return a list of property method name strings
        @return list of strings - Names of the property methods
        """
        return list(self.stringJasonData['propertyMethods'].keys())

    def getPropertyMethodData(self, methodName):
        """!
        @brief Return the input methodName data
        @return (tuple) - {string} Language descption property name,
                          {string} Brief description of the property method for Doxygen comment,
                          {list of dictionaries} Parameter list (probably empty list),
                          {dictionary} Return data dictionary
        """
        entry = self.stringJasonData['propertyMethods'][methodName]
        return entry['name'], entry['briefDesc'], entry['params'], entry['return']

    def _defineTranslationDict(self, translateBaseLang = "en", translateText = None):
        """!
        @brief Create a translation dictionary
        @param translateBaseLang {string} ISO 639-1 language code for the input translateText string
        @param translateText {list} Parsed text of the message
        @return dictionary - {'base':<translateBaseLang>, 'text':<translateText>} Translate method translation string dictionary
        """
        return {translateBaseLang: translateText}

    def addManualTranslation(self, methodName:str, baseLang:str = "en", textData = None):
        """!
        @brief Add language text to the function definition
        @param methodName {string} Translation method name to add the language text to
        @param baseLang {sting} ISO 639-1 language code for the input textData string
        @param textData {list} Parsed text of the message
        @return boolean - True if it was added, else false
        """
        if methodName in self.stringJasonData['translateMethods']:
            if textData is not None:
                self.stringJasonData['translateMethods'][methodName]['translateDesc'][baseLang] = textData
                return True
            else:
                return False
        else:
            return False

    def _translateText(self, sourceLang:str, targetLang:str, text:str):
        """!
        @brief Translate the input text
        @param sourceLang {string} ISO 639-1 language code of the input text
        @param targetLang {string} ISO 639-1 language code for the output text
        @param text {string} text to translate
        @return string - Translated text
        """
        from google.cloud import translate_v2 as translate
        if self.transClient is None:
            self.transClient = translate.Client()

        if isinstance(text, bytes):
            text = text.decode("utf-8")

        translatedTextData = self.transClient.translate(text,
                                                        target_language=targetLang,
                                                        format_='text',
                                                        source_language=sourceLang,
                                                        model='nmt')
        rawTranslatedText = translatedTextData['translatedText']
        return rawTranslatedText

    def _translateMethodText(self, methodName:str, jsonLangData:LanguageDescriptionList = None):
        """!
        @brief Add language text to the function definition
        @param methodName {string} Translation method name to add the language text to
        @apram jsonLangData {LanguageDescriptionList} Language list data
        """
        if jsonLangData is not None:
            # Get the list of supported languages and the list of existing translations
            languageList = jsonLangData.getLanguageList()
            existingLangages = list(self.stringJasonData['translateMethods'][methodName]['translateDesc'])

            # Determine if any language translations are missing
            for language in languageList:
                langIsoCode = jsonLangData.getLanguageIsoCodeData(language)
                if langIsoCode not in existingLangages:
                    # Use the first language
                    sourceLanguage = existingLangages[0]
                    baseTextData = self.stringJasonData['translateMethods'][methodName]['translateDesc'][sourceLanguage]
                    sourceText = StringClassNameGen.assembleParsedStrData(baseTextData)

                    # Translate and parse for storage
                    translatedText = self._translateText(sourceLanguage, langIsoCode, sourceText)
                    translatedTextData = StringClassNameGen.parseTranslateString(translatedText)
                    self.stringJasonData['translateMethods'][methodName]['translateDesc'][langIsoCode] = translatedTextData
        else:
            pass


    def _defineTranslateFunctionEntry(self, briefDesc = "", paramsList = [], retDesc = "",
                                      translateBaseLang = "en", translateText = None):
        """!
        @brief Define a property string return function dictionary and
               return the entry to the caller

        @param briefDesc {string} Brief description of the function used in
                                  doxygen comment block generation
        @param paramsList {list of dictionaries} List of the function parameter dictionary entrys
        @param retDesc {string} Description of the return parserstr value
        @param translateBaseLang {string} ISO 639-1 language code for the input translateText string
        @param translateText {list} Parsed text of the message

        @return {'name':<string>, 'briefDesc':<string>, 'params':[],
                 'return':ParamRetDict.buildReturnDict('text', retDesc, False),
                 'translateDesc': {'base':<string> 'text':<string>}} Translate function dictionary
        """
        functionDict = {'briefDesc': briefDesc,
                        'params': paramsList,
                        'return': ParamRetDict.buildReturnDict("text", retDesc, False),
                        'translateDesc': self._defineTranslationDict(translateBaseLang, translateText)
                        }
        return functionDict

    def getTranlateMethodList(self):
        """!
        @brief Return a list of property method name strings
        @return list of strings - Names of the property methods
        """
        return list(self.stringJasonData['translateMethods'].keys())

    def getTranlateMethodFunctionData(self, methodName):
        """!
        @brief Return the input methodName data
        @return (tuple) - {string} Brief description of the property method for Doxygen comment,
                          {list of dictionaries} Parameter list (probably empty list),
                          {dictionary} Return data dictionary
        """
        entry = self.stringJasonData['translateMethods'][methodName]
        return entry['briefDesc'], entry['params'], entry['return']

    def getTranlateMethodTextData(self, methodName, targetLanguage):
        """!
        @brief Return the input methodName data
        @param methodName (string) Name of the method to retrive data from
        @param targetLanguage (string) Name of the target language to retrive
        @return (tuple list) - Parsed text list
        """
        return self.stringJasonData['translateMethods'][methodName]['translateDesc'][targetLanguage]

    def _inputIsoTranslateCode(self):
        """!
        @brief Get the ISO 639-1 translate language code from user input and check for validity
        @return string - translate code
        """
        isoTranslateId = ""
        while(isoTranslateId == ""):
            transId = input("Enter original string ISO 639-1 translate language code (2 lower case characters): ").lower()

            # Check validity
            if re.match('^[a-z]{2}$', transId):
                # Valid name
                isoTranslateId = transId
            else:
                # invalid name
                print("Error: Only two characters a-z are allowed in the code, try again.")
        return isoTranslateId

    def _inputCName(self):
        paramName = ""
        while(paramName == ""):
            name = input("Enter parameter name: ")
            name.strip()

            # Check validity
            if re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                # Valid name
                paramName = name
            else:
                # invalid name
                print("Error: Must be a valid C name, try again.")
        return paramName

    def _inputCType(self):
        varType = ""
        while(varType == ""):
            inputType = input("Enter parameter type [T(ext)|i(nteger)|u(nsigned)|s(ize)|c(ustom)] : ").lower()

            # Check validity
            if (inputType == "s") or (inputType=="size"):
                varType = "size"
            elif (inputType == "t") or (inputType=="text"):
                varType = "string"
            elif (inputType == "i") or (inputType=="integer"):
                varType = "integer"
            elif (inputType == "u") or (inputType=="unsigned"):
                varType = "unsigned"
            elif (inputType == "c") or (inputType=="custom"):
                print ("Note: Custom type must have an operator<< defined.")
                customType = input("Enter custom parameter type: ")

                typeNames = customType.split("::")
                # Strip reference and pointer decorations
                typeNames[-1].rstrip('&')
                typeNames[-1].rstrip('*')
                for typeName in typeNames:
                    typeName.strip() # Remove whitespace
                    if re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', typeName):
                        # valid
                        varType = customType
                    else:
                        # invalid type
                        print (customType+" is not a valid c/c++ type name, try again.")
            else:
                # invalid name
                print("Error: \""+inputType+"\" unknown. Please select one of the options from the menu.")

        return varType

    def _inputParameterData(self):
        """!
        @brief Get input parameter data from user input
        @return dictionary - Param dictionary from  ParamRetDict.buildParamDict()
        """
        paramName = self._inputCName()
        paramType = self._inputCType()
        paramDesc = input("Enter brief parameter description for doxygen comment: ")
        return ParamRetDict.buildParamDict(paramName, paramType, paramDesc)

    def _inputReturnData(self):
        """!
        @brief Get the return data description from the user
        """
        retDesc = input("Enter brief description of the return value for doxygen comment: ")
        return retDesc

    def update(self):
        """!
        @brief Update the JSON file with the current contents of self.langJsonData
        """
        with open(self.filename, 'w', encoding='utf-8') as langJsonFile:
            json.dump(self.stringJasonData, langJsonFile, indent=2)

    def _validateTranslateString(self, paramList, testString):
        """!
        @brief Get the translation string template for the new translate function

        @param paramList {list of dictionaries} List of parameter description dictionaries
                                                for this function
        @param testString {string} String to check for validity

        @return boolean - True if string has all parameters correctly marked, else False
        @return number - Number of matched items
        @return number - Number of parameters found in the input string
        """
        # Construct the expected list
        expectedParamList = []
        for param in paramList:
            paramName = ParamRetDict.getParamName(param)
            expectedParamList.append(paramName)

        # Break the string into it's component parts
        parsedStrData = StringClassNameGen.parseTranslateString(testString)

        # Check the broken string counts
        matchCount = 0
        paramCount = 0
        for parsedData in parsedStrData:
            if StringClassNameGen.isParsedParamType(parsedData):
                paramCount +=1
                if StringClassNameGen.getParsedStrData(parsedData) in expectedParamList:
                    matchCount+=1

        if (matchCount == len(expectedParamList)) and (paramCount == matchCount):
            # Return success
            return True, matchCount, paramCount, parsedStrData
        else:
            # Return failure
            return False, matchCount, paramCount, parsedStrData

    def _inputTranslateString(self, paramList):
        """!
        @brief Get the translation string template for the new translate function

        @param paramList {list of dictionaries} List of parameter description dictionaries
                                                for this function

        @return string - Validated translation template string
        """
        # Build parameter list help string
        expectedParamHelp = ""
        prefix = ""
        for param in paramList:
            paramName = ParamRetDict.getParamName(param)
            expectedParamHelp += prefix
            expectedParamHelp += '@'
            expectedParamHelp += paramName
            expectedParamHelp += '@'
            prefix = " ,"

        # Get the translate string from the user
        stringValid = False
        translateString = ""

        while not stringValid:
            print("Enter translation template string. Use @paramName@ in the string to indicate where the ")
            print("function parameters should be inserted.")
            print("Example with single input parameter name \"keyString\": Found argument key @keyString@")
            translateString = input("String:")
            stringValid, matchCount, paramCount, parsedString = self._validateTranslateString(translateString)

            if not stringValid:
                if (len(paramList) > matchCount) and (len(paramList) > paramCount):
                    print ("Error: Template parameter missing, found "+str(paramCount-matchCount)+" of "+str(paramCount)+" expected template parameters.")
                elif (len(paramList) > matchCount) and (len(paramList) == paramCount):
                    print ("Error: Template parameter(s) misspelled, spelling error count "+str(paramCount-matchCount))
                elif (len(paramList) == matchCount) and (len(paramList) < paramCount):
                    print ("Error: Too many template parameters in input string, expected "+str(matchCount)+"found "+str(paramCount))
                else:
                    print ("Error: Translation template parameter list does not match expected.")
                    print ("   Found "+str(paramCount)+" parameters of expected "+str(len(paramList))+" parameters in string.")
                    print ("   Matched "+str(matchCount)+" parameters of expected "+str(len(paramList))+" parameters in string.")
                print("User input template:")
                print("    "+translateString)
                print("Expected parameter list:")
                print("    "+expectedParamHelp)

        return parsedString

    def newTranslateMethodEntry(self, languageList:LanguageDescriptionList = None):
        """!
        @brief Define and add a new translate string return function dictionary
               to the list of translate functions
        """
        newEntry = {}
        entryCorrect = False

        while not entryCorrect:
            methodName = self._inputCName()
            methodDesc = input("Enter brief function description for doxygen comment: ")

            paramList = []
            paramCount = input("Enter parameter count? [0-n]: ")
            while(paramCount > 0):
                paramList.append(self._inputParameterData())
                paramCount -= 1

            returnDesc = self._inputReturnData()

            languageBase = self._inputIsoTranslateCode()
            translateString = self._inputTranslateString(paramList)
            newEntry = self._defineTranslateFunctionEntry(methodDesc, paramList, returnDesc, languageBase, translateString)

            # Print entry for user to inspect
            print("New Entry:")
            print(newEntry)
            commit = input("Is this correct? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                entryCorrect = True

        # Test existing for match
        commitFlag = False
        if methodName in self.stringJasonData['translateMethods'].keys():
            # Determine if we should overwrite existing
            commit = input("Overwrite existing "+methodName+" entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                commitFlag = True
                self.stringJasonData['translateMethods'][methodName] = newEntry
                self._translateMethodText(methodName, languageList)
        else:
            commit = input("Add new entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                commitFlag = True
                self.stringJasonData['translateMethods'][methodName] = newEntry
                self._translateMethodText(methodName, languageList)

        return commitFlag

    def addTranslateMethodEntry(self, methodName:str, methodDesc:str, paramList:list,
                                returnDescription:str, isoLangCode:str, translateString:str,
                                override:bool = False, languageList:LanguageDescriptionList = None):
        """!
        @brief Add a new translate string return function dictionary
               to the list of translate functions
        @param methodName {string} Name of the function
        @param methodDesc {string} Brief description of the function for doxygen comment generation
        @param paramList {list of dictionaries} List of the input parameter description dictionaries
        @param returnDescription {string} Brief description of the return value for doxygen comment generation
        @param isoLangCode {string} ISO 639-1 language code of the input translateString
        @param translateString {string} String to generate translations for
        @param override {boolean} True = Override existing without asking
        @param languageList {LanguageDescriptionList | None} Supported language description data or None
        """
        status, matchCount, paramCount, parsedStrData = self._validateTranslateString(paramList, translateString)
        if not status:
            print ("Error: Invalid translation string: "+translateString+". paramCount= "+str(paramCount)+" matchCount= "+str(matchCount))
            return False

        newEntry = self._defineTranslateFunctionEntry(methodDesc, paramList, returnDescription, isoLangCode, parsedStrData)

        if methodName in self.stringJasonData['translateMethods'].keys():
            # Determine if we should overwrite existing
            if override:
                self.stringJasonData['translateMethods'][methodName] = newEntry
                self._translateMethodText(methodName, languageList)
            else:
                commit = input("Overwrite existing "+methodName+" entry? [Y/N]").upper()
                if ((commit == 'Y') or (commit == "YES")):
                    self.stringJasonData['translateMethods'][methodName] = newEntry
                    self._translateMethodText(methodName, languageList)
        else:
            self.stringJasonData['translateMethods'][methodName] = newEntry
            self._translateMethodText(methodName, languageList)

    def _getPropertyReturnData(self):
        """!
        @brief Get the property function return data and property name
        @return string, string, string, string - Language description property name,
                                                 Method name,
                                                 Method return type,
                                                 Return type description for Doxygen comment
                                                 True if return is a list, else False
        """
        propertyOptions = LanguageDescriptionList.getLanguagePropertyList()

        print ("Select language property, from options:")
        optionText = ""
        optionPrefix = "    "
        maxIndex = 0
        for index, propertyId in enumerate(propertyOptions):
            optionText +=  optionPrefix
            optionText += str(index)+": "
            optionText += propertyId
            optionPrefix = ", "
            maxIndex += 1
        print (optionText)

        propertyId = None
        while propertyId is None:
            propertyIndex = int(input("Enter property [0 - "+str(maxIndex-1)+"]: "))
            if (propertyIndex >= 0) and (propertyIndex < maxIndex):
                propertyId = propertyOptions[propertyIndex]
            else:
                print ("Valid input values are 0 to "+str(maxIndex-1)+", try again")

        returnType, returnDesc, isList = LanguageDescriptionList.getLanguagePropertyReturnData(propertyId)
        methodName = LanguageDescriptionList.getLanguagePropertyMethodName(propertyId)
        return propertyId, methodName, returnType, returnDesc, isList

    def newPropertyMethodEntry(self):
        """!
        @brief Define and add a property string return function dictionary and
               add it to the list of translate functions
        """
        newEntry = {}
        entryCorrect = False

        while not entryCorrect:
            propertyName, methodName, returnType, returnDesc, isList = self._getPropertyReturnData()
            methodDesc = "Get the "+returnDesc+" for this object"

            newEntry = self._definePropertyFunctionEntry(propertyName, methodDesc, returnType, returnDesc, isList)

            # Print entry for user to inspect
            print(methodName+":")
            print(newEntry)
            commit = input("Is this correct? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                entryCorrect = True

        # Check for existing for match
        commitFlag = False
        if methodName in self.stringJasonData['propertyMethods'].keys():
            # Determine if we should overwrite existing
            commit = input("Overwrite existing "+methodName+" entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                self.stringJasonData['propertyMethods'][methodName] = newEntry
                commitFlag = True
        else:
            # Determine if we should add the new entry
            commit = input("Add new entry? [Y/N]").upper()
            if ((commit == 'Y') or (commit == "YES")):
                self.stringJasonData['propertyMethods'][methodName] = newEntry
                commitFlag = True

        return commitFlag

    def addPropertyMethodEntry(self, propertyName, override = False):
        """!
        @brief Add a new translate string return function dictionary
               to the list of translate functions
        @param propertyName {string} LanguageDescriptionList.getLanguagePropertyList() property key
        @param override {boolean} True = Override existing without asking
        """
        # Make sure property exists in the language data
        propertyList = LanguageDescriptionList.getLanguagePropertyList()

        # Property exists, generate the new entry
        if propertyName in propertyList:
            returnType, returnDesc, isList = LanguageDescriptionList.getLanguagePropertyReturnData(propertyName)
            methodDesc = "Get the "+returnDesc+" for this object"
            methodName = LanguageDescriptionList.getLanguagePropertyMethodName(propertyName)

            newEntry = self._definePropertyFunctionEntry(propertyName, methodDesc, returnType, returnDesc)

            if methodName in self.stringJasonData['propertyMethods'].keys():
                # Verify the overwrite
                if override:
                    self.stringJasonData['propertyMethods'][methodName] = newEntry
                else:
                    commit = input("Overwrite existing "+methodName+" entry? [Y/N]").upper()
                    if ((commit == 'Y') or (commit == "YES")):
                        self.stringJasonData['propertyMethods'][methodName] = newEntry
            else:
                # Add the entry
                self.stringJasonData['propertyMethods'][methodName] = newEntry


def CreateDefaultStringFile(classStrings:StringClassDescription, languageList:LanguageDescriptionList, forceUpdate:bool = False):
    """!
    @brief Add a function to the self.langJsonData data
    @param classStrings {StringClassDescription} - Object to create/update
    @param languageList {LanguageDescriptionList} - List of languages to translate
    @param forceUpdate {boolean} True force the update without user intervention,
                                 False request update confermation on all methods
    """
    classStrings.addPropertyMethodEntry("isoCode", override = forceUpdate)

    # General argument parsing messages
    classStrings.addTranslateMethodEntry("getNotListTypeMessage", "Return non-list varg error message",
                                         [ParamRetDict.buildParamDict("nargs", "integer", "input nargs value")],
                                         "Non-list varg error message",
                                         "en",
                                         "Only list type arguments can have an argument count of @nargs@",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getUnknownArgumentMessage", "Return unknown parser key error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Unknown key")],
                                         "Unknown parser key error message",
                                         "en",
                                         "Unknown argument: @keyString@",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getInvalidAssignmentMessage", "Return varg invalid assignment error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key")],
                                         "Varg key invalid assignment error message",
                                         "en",
                                         "\"@keyString@\" invalid assignment",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getAssignmentFailedMessage", "Return varg assignment failed error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDict("valueString", "string", "Assignment value")],
                                         "Varg key assignment failed error message",
                                         "en",
                                         "\"@keyString@\", \"@valueString@\" assignment failed",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingAssignmentMessage", "Return varg missing assignment error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key")],
                                         "Varg key missing value assignment error message",
                                         "en",
                                         "\"@keyString@\" missing assignment value",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingListAssignmentMessage", "Return varg missing list value assignment error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDict("nargsExpected", "size", "Expected assignment list length"),
                                          ParamRetDict.buildParamDict("nargsFound", "size", "Input assignment list length")],
                                         "Varg key input value list too short error message",
                                         "en",
                                         "\"@keyString@\" missing assignment value(s). Expected: @nargsExpected@ found: @nargsFound@ arguments",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getTooManyAssignmentMessage", "Return varg missing list value assignment error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key"),
                                          ParamRetDict.buildParamDict("nargsExpected", "size", "Expected assignment list length"),
                                          ParamRetDict.buildParamDict("nargsFound", "size", "Input assignment list length")],
                                         "Varg key input value list too long error message",
                                         "en",
                                         "\"@keyString@\" too many assignment values. Expected: @nargsExpected@ found: @nargsFound@ arguments",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getMissingArgumentMessage", "Return required varg missing error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key")],
                                         "Required varg key missing error message",
                                         "en",
                                         "\"@keyString@\" required argument missing",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getArgumentCreationError", "Return parser add varg failure error message",
                                         [ParamRetDict.buildParamDict("keyString", "string", "Error key")],
                                         "Parser varg add failure message",
                                         "en",
                                         "Argument add failed: @keyString@",
                                         override = forceUpdate,
                                         languageList = languageList)

    # Command Line parser messages
    classStrings.addTranslateMethodEntry("getUsageMessage", "Return usage help message",
                                         [],
                                         "Usage help message",
                                         "en",
                                         "Usage:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getPositionalArgumentsMessage", "Return positional argument help message",
                                         [],
                                         "Positional argument help message",
                                         "en",
                                         "Positional Arguments:",
                                         override = forceUpdate,
                                         languageList = languageList)


    classStrings.addTranslateMethodEntry("getSwitchArgumentsMessage", "Return optional argument help message",
                                         [],
                                         "Optional argument help message",
                                         "en",
                                         "Optional Arguments:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getHelpString", "Return default help switch help message",
                                         [],
                                         "Default help argument help message",
                                         "en",
                                         "show this help message and exit",
                                         override = forceUpdate,
                                         languageList = languageList)

    # Environment parser messages
    classStrings.addTranslateMethodEntry("getEnvArgumentsMessage", "Return environment parser argument help header",
                                         [],
                                         "Environment parser argument help header message",
                                         "en",
                                         "Defined Environment values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getEnvironmentNoFlags", "Return environment parser add flag varg failure error message",
                                         [ParamRetDict.buildParamDict("envKeyString", "string", "Flag key")],
                                         "Environment parser add flag varg failure message",
                                         "en",
                                         "Environment value @envKeyString@ narg must be > 0",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.addTranslateMethodEntry("getRequiredEnvironmentArgMissing", "Return environment parser required varg missing error message",
                                         [ParamRetDict.buildParamDict("envKeyString", "string", "Flag key")],
                                         "Environment parser required varg missing error message",
                                         "en",
                                         "Environment value @envKeyString@ must be defined",
                                         override = forceUpdate,
                                         languageList = languageList)


    # JSON file parser messages
    classStrings.addTranslateMethodEntry("getJsonArgumentsMessage", "Return json parser argument help header",
                                         [],
                                         "JSON parser argument help header message",
                                         "en",
                                         "Available JSON argument values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    # XML file parser messages
    classStrings.addTranslateMethodEntry("getXmlArgumentsMessage", "Return xml parser argument help header",
                                         [],
                                         "XML parser argument help header message",
                                         "en",
                                         "Available XML argument values:",
                                         override = forceUpdate,
                                         languageList = languageList)

    classStrings.update()

def AddTranslateMethodEntry(classStrings:StringClassDescription, languageList:LanguageDescriptionList):
    """!
    @brief Add a translate string function to the self.langJsonData data
    @param classStrings (StringClassDescription) - Object to add translate method to
    """
    commit = classStrings.newTranslateMethodEntry(languageList)
    if commit:
        print ("Updating JSON file")
        classStrings.update()

def AddPropertyMethodEntry(classStrings:StringClassDescription):
    """!
    @brief Add a property string function to the self.langJsonData data
    """
    commit = classStrings.newPropertyMethodEntry()
    if commit:
        print ("Updating JSON file")
        classStrings.update()

def PrintMethods(classStrings:StringClassDescription):
    """!
    @brief Print the current data file
    @param classStrings (StringClassDescription) - Object to output
    """
    print(classStrings.stringJasonData)

def CommandMain():
    """!
    Utility command interface
    @param subcommand {string} JSON string file command
    """
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(prog="jsonStringClassDescription",
                                     description="Update argpaser library language description JSON file")
    parser.add_argument('-p','--path', dest='jsonpath', required=False, type=pathlib.Path,
                        default='../data', help='Existing destination directory')
    parser.add_argument('subcommand', choices=['addproperty', 'addtranslate', 'print', 'createnew'])
    parser.add_argument('-f', dest='force', action='store_true', default=False)
    args = parser.parse_args()

    classStrings = StringClassDescription(FileNameGenerator.getStringClassDescriptionFileName(args.jsonpath))
    languageData = LanguageDescriptionList(FileNameGenerator.getLanguageDescriptionFileName(args.jsonpath))

    if args.subcommand.lower() == "addproperty":
        AddPropertyMethodEntry(classStrings)
    if args.subcommand.lower() == "addtranslate":
        AddTranslateMethodEntry(classStrings, languageData)
    elif args.subcommand.lower() == "print":
        PrintMethods(classStrings)
    elif args.subcommand.lower() == "createnew":
        CreateDefaultStringFile(classStrings, languageData, args.force)
    else:
        print ("Error: Unknown JSON string method definition file command: "+args.subcommand)
        SystemExit(1)


if __name__ == '__main__':
    CommandMain()