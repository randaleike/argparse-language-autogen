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

from .json_data.param_return_tools import ParamRetDict
from .common.cpp_file_gen_base import GenerateCppFileHelper

class BaseStringClassGenerator(GenerateCppFileHelper):
    def __init__(self, owner:str|None = None, eulaName:str|None = None,
                 baseClassName:str = "BaseClass", dynamicCompileSwitch:str = "DYNAMIC_INTERNATIONALIZATION"):
        """!
        @brief GenerateOSLanguageDetectFiles constructor
        @param owner {string} Owner string for the copyright/EULA file header comment
        @param eulaName {string} EULA name for the copyright/EULA file header comment
        """
        super().__init__(eulaName)
        if owner is None:
            self.owner = "Unknown"
        else:
            self.owner = owner

        self.baseClassName = baseClassName
        self.dynamicCompileSwitch = dynamicCompileSwitch

        # modify the type translation matrix
        self.typeXlationDict['string'] = "parserstr"
        self.typeXlationDict['text'] = "parserstr"

        # Add the specialty types
        self.baseIntfRetPtrType = "std::shared_ptr<"+self.baseClassName+">"
        self.typeXlationDict['LANID'] = "LANGID"
        self.typeXlationDict['sharedptr'] = self.baseIntfRetPtrType
        self.typeXlationDict['char'] = "parserchar"
        self.typeXlationDict['strstream'] = "parser_str_stream"

        self.baseIntfRetPtrDict = ParamRetDict.buildReturnDict('sharedptr',
                                                                "Shared pointer to "+self.baseClassName+"<lang> based on OS local language")

        self.versionMajor = 1
        self.versionMinor = 0
        self.versionPatch = 0
        self.versionTweak = 0
        self.autoToolName = self.__class__.__name__+self._getVersion()

        self.groupName = "LocalLanguageSelection"
        self.groupDesc = "Local language detection and selection utility"

        self.ifDynamicDefined = "defined("+self.dynamicCompileSwitch+")"
        self.declareIndent = 8
        self.functionIndent = 4

    def _getParserStringType(self)->str:
        return "parserstr"

    def _getParserCharType(self)->str:
        return "parserchar"

    def _getParserStrStreamType(self)->str:
        return "parser_str_stream"

    def _genMakePtrReturnStatement(self, classMod:str|None = None)->str:
        """!
        @brief Generate a language select return statement
        @param classMod {string} Language name of the final parser string object
        @return string cpp code
        """
        if classMod is not None:
            ptrName = self.baseClassName+classMod.capitalize()
        else:
            ptrName = self.baseClassName

        retLine = "return std::make_shared<"
        retLine += ptrName
        retLine += ">();\n"
        return retLine

    def _getVersion(self)->str:
        return "V"+str(self.versionMajor)+"."+str(self.versionMinor)+"."+str(self.versionPatch)+"."+str(self.versionTweak)

    def _generateFileHeader(self)->list:
        """!
        @brief Generate the boiler plate file header with copyright and eula
        """
        return super()._generateGenericFileHeader(self.autoToolName, 2025, self.owner)

    def _generateHFileName(self, langName:str|None = None)->str:
        if langName is not None:
            return self.baseClassName+langName.capitalize()+".h"
        else:
            return self.baseClassName+".h"

    def _generateCppFileName(self, langName:str|None = None)->str:
        if langName is not None:
            return self.baseClassName+langName.capitalize()+".cpp"
        else:
            return self.baseClassName+".cpp"

    def _generateUnittestFileName(self, langName:str|None = None)->str:
        if langName is not None:
            return self.baseClassName+langName.capitalize()+"_test.cpp"
        else:
            return self.baseClassName+"_test.cpp"

    def _generateUnittestTargetName(self, langName:str|None = None)->str:
        if langName is not None:
            return self.baseClassName+langName.capitalize()+"_test"
        else:
            return self.baseClassName+"_test"

    def _generateMockHFileName(self, langName:str|None = None)->str:
        if langName is not None:
            return "mock_"+self.baseClassName+langName.capitalize()+".h"
        else:
            return "mock_"+self.baseClassName+".h"

    def _generateMockCppFileName(self, langName:str|None = None)->str:
        if langName is not None:
            return "mock_"+self.baseClassName+langName.capitalize()+".cpp"
        else:
            return "mock_"+self.baseClassName+".cpp"

    def _writeMethod(self, methodName:str, methodDesc:str,
                     methodParams:list, returnDict:dict, prefix:str|None, postfix:str|None,
                     skipDoxygenComment:bool = True, inlineCode:list|None = None)->list:
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
        if len(methodParams) == 0:
            if postfix is not None:
                postfixFinal = "const " + postfix
            else:
                postfixFinal = "const"
        else:
            postfixFinal = postfix

        # Output final declaration
        declText = self._declareFunctionWithDecorations(methodName,
                                                        methodDesc,
                                                        methodParams,
                                                        returnDict,
                                                        self.declareIndent,
                                                        skipDoxygenComment,
                                                        prefix,
                                                        postfixFinal,
                                                        inlineCode)

        return declText

    def _writeMockMethod(self, methodName:str, methodParams:list, returnDict:dict, postfix:str|None)->list:
        """!
        @brief Write the property method definitions

        @param methodName {string} Property method name
        @param methodParams {list of dictionaries} Method input parameter definitions(s)
        @param returnDict {dictionary} Return data definition
        @param postfix {string} Method declaration postfix

        @return list of strings - Mock method declaration
        """
        # Translate the param data
        if len(methodParams) == 0:
            if postfix is not None:
                postfixFinal = "const, " + postfix
            else:
                postfixFinal = "const"
        else:
            postfixFinal = postfix

        # Output mock declaration
        declText = "".rjust(self.declareIndent, ' ')
        declText += "MOCK_METHOD("
        declText += self._declareType(ParamRetDict.getReturnType(returnDict), ParamRetDict.getParamTypeMod(returnDict))
        declText += ", "
        declText += methodName
        declText += ", "

        # Add the parameters
        declText += self._genFunctionParams(methodParams)

        # Add the post fix data
        if postfixFinal is not None:
            declText += ", ("
            declText += postfixFinal
            declText += ")"

        # Close the MOCK_METHOD macro and out put to file
        declText += ");\n"
        return [declText]
