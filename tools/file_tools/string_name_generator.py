"""@package argparselangautogen
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

class StringClassNameGen(object):
    projectNameSpace = "argparser"

    parsedTypeText    = 'text'
    parsedTypeParam   = 'param'
    parsedTypeSpecial = 'special'

    """!
    @brief Helper static class for generating consistent ParserStringInterface names across multiple files
    """
    def __init__(self):
        pass

    @staticmethod
    def getNamespaceName():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return StringClassNameGen.projectNameSpace

    @staticmethod
    def getBaseClassName():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return "ParserStringListInterface"

    @staticmethod
    def getBaseClassNameWithNamespace():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return StringClassNameGen.getNamespaceName()+"::"+StringClassNameGen.getBaseClassName()

    @staticmethod
    def getLangClassName(lang):
        """!
        @brief Build the language specific file name based on the input lang value
        @param lang {string} Language name
        @return string Language specific class name
        """
        return StringClassNameGen.getBaseClassName()+lang.capitalize()

    @staticmethod
    def getParserStringType():
        return "parserstr"

    @staticmethod
    def getParserCharType():
        return "parserchar"

    @staticmethod
    def getParserStrStreamType():
        return "parser_str_stream"

    @staticmethod
    def getDynamicCompileswitch():
        """!
        @brief Return the base class name
        @return string Base sting class name
        """
        return "DYNAMIC_INTERNATIONALIZATION"

    @staticmethod
    def makeTextEntry(textBlock:str):
        return (StringClassNameGen.parsedTypeText, textBlock)

    @staticmethod
    def makeSpecialCharEntry(textBlock:str):
        return (StringClassNameGen.parsedTypeSpecial, textBlock[0])

    @staticmethod
    def makeParamEntry(paramName:str):
        return (StringClassNameGen.parsedTypeParam, paramName)

    @staticmethod
    def parseTextBlock(textBlock:str):
        """!
        @brief Convert the input string to an output string stream
        @param baseString {string} String to convert
        @return list of dictionaries - List of dictionary entries descibing the parsed string
        """
        matchList = re.finditer(r'\\|\"', textBlock)

        stringList = []
        previousEnd = 0
        for matchData in matchList:
            # Add text data prior to first match if any
            if matchData.start() > previousEnd:
                rawText = r'{}'.format(textBlock[previousEnd:matchData.start()])
                stringList.append(StringClassNameGen.makeTextEntry(rawText))

            # Add the matched parameter
            stringList.append(StringClassNameGen.makeSpecialCharEntry(matchData.group()))
            previousEnd = matchData.end()

        # Add the trailing string
        if previousEnd < len(textBlock):
            rawText = r'{}'.format(textBlock[previousEnd:])
            stringList.append(StringClassNameGen.makeTextEntry(rawText))

        return stringList

    @staticmethod
    def parseTranslateString(baseString:str):
        """!
        @brief Convert the input string to an output string stream
        @param baseString {string} String to convert
        @return list of tuples - List of tuples descibing the parsed string
                                 tuple[0] = type, StringClassNameGen.parsedTypeText or StringClassNameGen.parsedTypeParam
                                 tuple[1] = data, if StringClassNameGen.parsedTypeText = text string
                                                  if StringClassNameGen.parsedTypeParam = parameter name
        """
        matchList = re.finditer(r'@[a-zA-Z_][a-zA-Z0-9_]*@', baseString)

        stringList = []
        previousEnd = 0
        for matchData in matchList:
            # Add text data prior to first match if any
            if matchData.start() > previousEnd:
                rawText = r'{}'.format(baseString[previousEnd:matchData.start()])
                stringList.extend(StringClassNameGen.parseTextBlock(rawText))

            # Add the matched parameter
            stringList.append(StringClassNameGen.makeParamEntry(matchData.group()[1:-1]))
            previousEnd = matchData.end()

        # Add the trailing string
        if previousEnd < len(baseString):
            rawText = r'{}'.format(baseString[previousEnd:])
            stringList.extend(StringClassNameGen.parseTextBlock(rawText))

        return stringList

    @staticmethod
    def assembleParsedStrData(stringTupleList:list):
        """!
        @brief Assemble the input string description tuple list into a translation string
        @param stringTupleList (list) List of string description tuples
        @return string - Assempled text string ready for input into a language translation engine
        """
        returnText = ""
        for descType, descData in stringTupleList:
            if StringClassNameGen.parsedTypeText == descType:
                returnText += descData
            elif StringClassNameGen.parsedTypeParam == descType:
                returnText += '@'
                returnText += descData
                returnText += '@'
            elif StringClassNameGen.parsedTypeSpecial == descType:
                returnText += descData
            else:
                raise TypeError("Unknown string description tuple type: "+descType)

        return returnText

    @staticmethod
    def assembleStream(stringTupleList:list):
        """!
        @brief Assemble the input string description tuple list into a translation string
        @param stringTupleList (list) List of string description tuples
        @return string - Assempled text string ready for input into a language translation engine
        """
        returnText = ""
        stringOpen = False

        for descType, descData in stringTupleList:
            if StringClassNameGen.parsedTypeText == descType:
                if not stringOpen:
                    returnText += " << \""
                    stringOpen = True
                returnText += descData
            elif StringClassNameGen.parsedTypeParam == descType:
                if stringOpen:
                    returnText += "\" << "
                    stringOpen = False
                returnText += descData
            elif StringClassNameGen.parsedTypeSpecial == descType:
                if not stringOpen:
                    returnText += " << \""
                    stringOpen = True
                returnText += "\\"+descData
            else:
                raise TypeError("Unknown string description tuple type: "+descType)

        # Close the open string if present
        if stringOpen:
            returnText += "\""
            stringOpen = False
        return returnText

    @staticmethod
    def assembleTestReturnString(stringTupleList:list, valueXlateDict:dict):
        """!
        @brief Assemble the input string description tuple list into a translation string
        @param stringTupleList (list) List of string description tuples
        @param valueXlateDict (dict) Dictionary of param names and expected values
        @return string - Assempled text string ready for input into a language translation
                         expected string
        """
        returnText = ""
        for descType, descData in stringTupleList:
            if StringClassNameGen.parsedTypeText == descType:
                returnText += descData
            elif StringClassNameGen.parsedTypeParam == descType:
                returnText += valueXlateDict[descData]
            elif StringClassNameGen.parsedTypeSpecial == descType:
                returnText += "\\"+descData
            else:
                raise TypeError("Unknown string description tuple type: "+descType)
        return returnText

    @staticmethod
    def isParsedTextType(parsedTuple:list):
        """!
        @brief Check if the input pgetParsedStrDataarsed translation string tuple is a text type
        @return boolean - True if tuple[0] == StringClassNameGen.parsedTypeText
                          else False
        """
        if parsedTuple[0] == StringClassNameGen.parsedTypeText:
            return True
        else:
            return False

    @staticmethod
    def isParsedParamType(parsedTuple:list):
        """!
        @brief Check if the input parsed translation string tuple is a text type
        @return boolean - True if tuple[0] == StringClassNameGen.parsedTypeParam
                          else False
        """
        if parsedTuple[0] == StringClassNameGen.parsedTypeParam:
            return True
        else:
            return False

    @staticmethod
    def getParsedStrData(parsedTuple:list):
        """!
        @brief Check if the input parsed translation string tuple is a text type
        @return string - paredTuple data field
        """
        return parsedTuple[1]
