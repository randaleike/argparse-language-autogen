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

from .common.param_return_tools import ParamRetDict
from .common.file_gen_tools import GenerateCppFileHelper
from .common.doxygen_gen_tools import CDoxyCommentGenerator

from .string_name_generator import StringClassNameGen

class BaseCppClassGenerator(GenerateCppFileHelper):
    """!
    @brief Helper methods for OS lang file function generation

    This class extends GenCFunctionHelper and implents some common data and functionality
    for specific OS language function implementations
    """
    def __init__(self, eulaName = None, baseClassName = "ParserStringListInterface"):
        """!
        @brief BaseCppClassGenerator constructor
        @param baseClassName {string} - Name of the base class for share_ptr generation
        """
        super().__init__(eulaName)

        self.baseClassName = baseClassName
        self.stdPtrType = "std::shared_ptr"
        self.returnType = self.stdPtrType+"<"+self.baseClassName+">"
        self.retPtrDict = ParamRetDict.buildReturnDict(self.returnType,
                                                       "Shared pointer to "+self.baseClassName+"<lang> based on OS local language")
        self.xlateMatrix = {'string':   {'type':"parserstr", 'isText':True },
                            'text':     {'type':"parserstr", 'isText':True },
                            'size':     {'type':"size_t",    'isText':False},
                            'integer':  {'type':"int",       'isText':False},
                            'unsigned': {'type':"unsigned",  'isText':False},
                            'LANID':    {'type':"LANGID",    'isText':False}}

    def _genFunctionDeclare(self, name, briefDesc, paramDictList, indent = 0):
        """!
        @brief Get the function declaration string for the given name

        @param name {string} Function name
        @param briefDesc {string} Brief description for DOXYGEN commant
        @param paramDictList {list} Parameter description dicionary list

        @return string list - Function comment block and declaration start
        """
        return self.declareFunctionWithDecorations(name, briefDesc, paramDictList, self.retPtrDict, indent)

    def _genFunctionDefine(self, name, briefDesc, paramDictList):
        """!
        @brief Get the function definition string for the given name

        @param name {string} Function name
        @param briefDesc {string} Brief description for DOXYGEN commant
        @param paramDictList {list} Parameter description dicionary list

        @return string list - Function comment block and declaration start
        """
        functionDef = self.defineFunctionWithDecorations(name, briefDesc, paramDictList, self.retPtrDict)
        functionDef.append("{\n")
        return functionDef

    def genMakePtrReturnStatement(self, classMod = None):
        """!
        @brief Generate a language select return statement
        @param classMod {string} Language name of the final parser string object
        """
        if classMod is not None:
            ptrName = self.baseClassName+classMod.capitalize()
        else:
            ptrName = self.baseClassName

        retLine = "return std::make_shared<"
        retLine += ptrName
        retLine += ">();\n"
        return retLine

    def genPtrParameterStatement(self, paramName):
        """!
        @brief Generate a language select variable declaration
        @param paramName {string} Variable name
        """
        paramLine = self.returnType
        paramLine += " "
        paramLine += paramName
        paramLine += ";\n"
        return paramLine

    def getParserStringType(self):
        return "parserstr"

    def declareStringListType(self):
        return self.declareListType(self.getParserStringType())

    def declareLANGIDListType(self):
        return self.declareListType("LANGID")

    def xlateGenericType(self, genericType, islist=False):
        """!
        @brief Translate the generic type specification to the CPP equivilent
        @param genericType {string} Generic type name
        @param islist {boolean} True if type is a list type, false if it a single value
        @return tuble (string, boolean) CPP type spcification
                                        True if value is text, else false
        """
        if islist:
            if genericType in self.xlateMatrix.keys():
                return self.declareListType(self.xlateMatrix[genericType]['type']), self.xlateMatrix[genericType]['isText']
            else:
                # Unknown return the same type name
                return self.declareListType(genericType), False
        else:
            if genericType in self.xlateMatrix.keys():
                return self.xlateMatrix[genericType]['type'], self.xlateMatrix[genericType]['isText']
            else:
                # Unknown return the same type name
                return genericType, False

    def xlateReturnDict(self, genericReturnDict):
        """!
        @brief Translate the input generic return dictionary object into
               the argparse C code type
        @param genericReturnDict {dictionary} Return data dictionary from the JSON file
        @return tuble (dictionary, boolean) - C translated return dictionary
                                              True if value is text, else false
        """
        retType, retDesc, isList = ParamRetDict.getReturnData(genericReturnDict)
        xlatedRetType, isText = self.xlateGenericType(retType, isList)
        return ParamRetDict.buildReturnDict(xlatedRetType, retDesc, isList), isText

    def xlateParamDict(self, genericParamDict):
        """!
        @brief Translate the input generic param dictionary object into
               the argparse C code type
        @param genericParamDict {dictionary} Param data dictionary from the JSON file
        @return tuble (dictionary, boolean) - C translated param dictionary
                                              True if value is text, else false
        """
        paramName, paramType, paramDesc, isList = ParamRetDict.getParamData(genericParamDict)
        xlatedRetType, isText = self.xlateGenericType(paramType, isList)
        return ParamRetDict.buildParamDict(paramName, xlatedRetType, paramDesc, isList), isText

    def xlateParamList(self, genericParamList):
        """!
        @brief Translate the input generic param dictionary list object into
               the argparse C code type
        @param genericParamList {list of dictionaries} Param data dictionary list from the JSON file
        @return list - C translated param dictionary list
        """
        xlatedParamList = []
        for paramDict in genericParamList:
            xlatedDict, isText = self.xlateParamDict(paramDict)
            xlatedParamList.append(xlatedDict)
        return xlatedParamList

class BaseStringClassGenerator(BaseCppClassGenerator):
    def __init__(self, owner = None, eulaName = None):
        """!
        @brief GenerateOSLanguageDetectFiles constructor
        @param owner {string} Owner string for the copyright/EULA file header comment
        @param eulaName {string} EULA name for the copyright/EULA file header comment
        """
        super().__init__(eulaName, StringClassNameGen.getBaseClassName())
        self.owner = owner
        self.versionMajor = 1
        self.versionMinor = 0
        self.versionPatch = 0
        self.versionTweak = 0
        self.autoToolName = self.__class__.__name__+self.getVersion()

        self.doxyCommentGen = CDoxyCommentGenerator()
        self.groupName = "LocalLanguageSelection"
        self.groupDesc = "Local language detection and selection utility"

        self.ifDynamicDefined = "defined("+StringClassNameGen.getDynamicCompileswitch()+")"
        self.declareIndent = 8
        self.functionIndent = 4

    def getVersion(self):
        return "V"+str(self.versionMajor)+"."+str(self.versionMinor)+"."+str(self.versionPatch)+"."+str(self.versionTweak)

    def _generateFileHeader(self):
        """!
        @brief Generate the boiler plate file header with copyright and eula
        """
        return super()._generateGenericFileHeader(self.autoToolName, 2025, self.owner)

    def _generateHFileName(self, langName = None):
        if langName is not None:
            return StringClassNameGen.getLangClassName(langName)+".h"
        else:
            return StringClassNameGen.getBaseClassName()+".h"

    def _generateCppFileName(self, langName = None):
        if langName is not None:
            return StringClassNameGen.getLangClassName(langName)+".cpp"
        else:
            return StringClassNameGen.getBaseClassName()+".cpp"

    def _generateUnittestFileName(self, langName = None):
        if langName is not None:
            return StringClassNameGen.getLangClassName(langName)+"_test.cpp"
        else:
            return StringClassNameGen.getBaseClassName()+"_test.cpp"

    def _generateUnittestTargetName(self, langName = None):
        if langName is not None:
            return StringClassNameGen.getLangClassName(langName)+"_test"
        else:
            return StringClassNameGen.getBaseClassName()+"_test"

    def _generateMockHFileName(self, langName = None):
        if langName is not None:
            return "mock_"+StringClassNameGen.getLangClassName(langName)+".h"
        else:
            return "mock_"+StringClassNameGen.getBaseClassName()+".h"

    def _writeMethod(self, methodName, methodDesc,
                     methodParams, returnDict, prefix, postfix,
                     skipDoxygenComment = True, inlineCode = None):
        """!
        @brief Write the property method definitions

        @param methodName {string} Property method name
        @param methodDesc {string} Property description for doxygen comment block
        @param methodParams {list of dictionaries} Method input parameter definitions(s)
        @param returnDict {dictionary} Return data definition
        @param prefix {string} Method declaration prefix
        @param postfix {string} Method declaration postfix
        @param skipDoxygenComment {boolean} True = skip doxygen method comment generation, False = generate doxygen method comment
        @param inlineCode {list of strings} Inline code strings or None if there is no inline code

        @return list of strings
        """
        # Translate the return type
        xlatedRetDict, isText = self.xlateReturnDict(returnDict)

        # Translate the param data
        xlatedParams = []
        if len(methodParams) == 0:
            if postfix is not None:
                postfixFinal = "const " + postfix
            else:
                postfixFinal = "const"
        else:
            postfixFinal = postfix
            xlatedParams = self.xlateParamList(methodParams)

        # Output final declaration
        declText = self.declareFunctionWithDecorations(methodName,
                                                       methodDesc,
                                                       xlatedParams,
                                                       xlatedRetDict,
                                                       self.declareIndent,
                                                       skipDoxygenComment,
                                                       prefix,
                                                       postfixFinal,
                                                       inlineCode)

        return declText

    def _writeMockMethod(self, methodName, methodParams, returnDict, postfix):
        """!
        @brief Write the property method definitions

        @param methodName {string} Property method name
        @param methodParams {list of dictionaries} Method input parameter definitions(s)
        @param returnDict {dictionary} Return data definition
        @param postfix {string} Method declaration postfix

        @return list of strings - Mock method declaration
        """
        # Translate the return type
        xlatedRetDict, isText = self.xlateReturnDict(returnDict)

        # Translate the param data
        xlatedParams = []
        if len(methodParams) == 0:
            if postfix is not None:
                postfixFinal = "const, " + postfix
            else:
                postfixFinal = "const"
        else:
            postfixFinal = postfix
            xlatedParams = self.xlateParamList(methodParams)

        # Output mock declaration
        declText = "".rjust(self.declareIndent, ' ')
        declText += "MOCK_METHOD("
        declText += ParamRetDict.getReturnType(xlatedRetDict)
        declText += ", "
        declText += methodName
        declText += ", "

        # Add the parameters
        declText += self.genFunctionParams(xlatedParams)

        # Add the post fix data
        if postfixFinal is not None:
            declText += ", ("
            declText += postfixFinal
            declText += ")"

        # Close the MOCK_METHOD macro and out put to file
        declText += ");\n"
        return [declText]
