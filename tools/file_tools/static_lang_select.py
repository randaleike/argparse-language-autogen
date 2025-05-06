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

from .json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from .common.doxygen_gen_tools import CDoxyCommentGenerator
from .string_class_tools import BaseStringClassGenerator

class StaticLangSelectFunctionGenerator(BaseStringClassGenerator):
    """!
    Methods for compile switch determined language select function generation
    """
    def __init__(self, jsonLangData:LanguageDescriptionList, owner:str|None = None, eulaName:str|None = None, baseClassName:str = "BaseClass",
                 dynamicCompileSwitch:str = "DYNAMIC_INTERNATIONALIZATION"):
        """!
        @brief StaticLangSelectFunctionGenerator constructor
        @param jsonLangData {string} JSON language description list file name
        @param owner {string|None} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string|None} Name of the EULA to pass down to the BaseStringClassGenerator parent
        @param baseClassName {string} Name of the base class for name generation
        @param dynnamicCompileSwitch {string} Dynamic compile switch for #if generation
        """
        super().__init__(owner, eulaName, baseClassName, dynamicCompileSwitch)
        self.selectFunctionName = "get"+baseClassName+"_Static"

        self.defStaticString = "!defined("+dynamicCompileSwitch+")"
        self.langJsonData = jsonLangData
        self.doxyCommentGen = CDoxyCommentGenerator()

    def getFunctionName(self)->str:
        return self.selectFunctionName

    def getOsDefine(self)->str:
        return self.defStaticString

    def getOsDynamicDefine(self)->str:
        return self.defStaticString

    def genFunctionDefine(self)->list:
        """!
        @brief Get the function declaration string for the given name
        @return string list - Function comment block and declaration start
        """
        codeList = self._defineFunctionWithDecorations(self.selectFunctionName,
                                                       "Determine the correct local language class from the compile switch setting",
                                                       [],
                                                       self.baseIntfRetPtrDict)
        codeList.append("{\n")
        return codeList

    def genFunctionEnd(self)->str:
        """!
        @brief Get the function declaration string for the given name
        @return string - Function close with comment
        """
        return self._endFunction(self.selectFunctionName)

    def genFunction(self, outfile):
        """!
        @brief Generate the function body text

        @param outfile {file} File to output the function to
        """
        # Generate the #if and includes
        functionBody = []
        functionBody.append("#if "+self.defStaticString+"\n")

        # Generate function doxygen comment and start
        functionBody.extend(self.genFunctionDefine())

        # Start function body generation
        bodyIndent = "".rjust(4, " ")

        # Generate #if #elf compile switch chain for each language in the dictionary
        firstLoop = True
        for langName in self.langJsonData.getLanguageList():
            ifline = "  "
            if firstLoop:
                ifline += "#if "
                firstLoop = False
            else:
                ifline += "#elif "
            ifline += "defined("+self.langJsonData.getLanguageCompileSwitchData(langName)+")\n"
            functionBody.append(ifline)
            functionBody.append(bodyIndent+self._genMakePtrReturnStatement(langName))

        # Add the final #else case
        functionBody.append("  #else //undefined language compile switch, use default\n")
        functionBody.append(bodyIndent+"#error one of the language compile switches must be defined\n")
        functionBody.append("  #endif //end of language #if/#elifcompile switch chain\n")

        # Complete the function
        functionBody.append(self.genFunctionEnd())
        functionBody.append("#endif // "+self.defStaticString+"\n")
        outfile.writelines(functionBody)

    def genReturnFunctionCall(self, indent:int = 4)->list:
        """!
        @brief Generate the call code for the linux dynamic lang selection function
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        doCall = indentText+"return "+self.selectFunctionName+"();\n"
        return [doCall]

    def genExternDefinition(self)->str:
        """!
        @brief Return the external function definition
        @return string - External function definition line
        """
        externDef = "extern "
        externDef += self.baseIntfRetPtrType
        externDef += " "
        externDef += self.selectFunctionName
        externDef += "();\n"
        return externDef

    def genUnitTest(self, getIsoMethod:str, outfile):
        """!
        @brief Generate all unit tests for the selection function

        @param getIsoMethod {string} Name of the ParserStringListInterface return ISO code method
        @param outfile {file} File to output the function to
        """
        # Generate block start code
        blockStart = []
        blockStart.append("#if ("+self.defStaticString+"\n")
        blockStart.append(self.genExternDefinition())
        outfile.writelines(blockStart)

        # Generate the testgenDoxyMethodComment
        breifDesc = "Test "+self.selectFunctionName+" selection case"
        testHeader = self.doxyCommentGen.genDoxyMethodComment(breifDesc, [])
        outfile.writelines(testHeader)

        # Generate the tests
        bodyIndent = "".rjust(4, " ")
        testVar = "testVar"
        testVarDecl = self.baseIntfRetPtrType+" "+testVar
        testVarTest = testVar+"->"+getIsoMethod+"().c_str()"

        for langName in self.langJsonData.getLanguageList():
            testBody = []
            testBody.append("#if defined("+self.langJsonData.getLanguageCompileSwitchData(langName)+")\n")
            testBody.append("TEST(StaticSelectFunction"+langName.capitalize()+", CompileSwitchedValue)\n")
            testBody.append("{\n")
            testBody.append(bodyIndent+"// Generate the test language string object\n")
            testBody.append(bodyIndent+testVarDecl+" = "+self.selectFunctionName+"();\n")
            testBody.append(bodyIndent+"EXPECT_STREQ(\""+self.langJsonData.getLanguageIsoCodeData(langName)+"\", "+testVarTest+";\n")
            # Complete the function
            testBody.append("}\n")
            testBody.append("#endif //end of #if defined("+self.langJsonData.getLanguageCompileSwitchData(langName)+")\n")
            testBody.append("\n") # whitespace for readability

            outfile.writelines(testBody)

        # Generate block end code
        outfile.writelines(["#endif // "+self.defStaticString+"\n"])

    def genUnitTestFunctionCall(self, checkVarName:str, indent:int = 4)->list:
        """!
        @brief Generate the call code for the linux dynamic lang selection unit test
        @param checkVarName {string} Unit test expected variable name
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        doCall = indentText+self.baseIntfRetPtrType+" "+checkVarName+" = "+self.selectFunctionName+"();\n"
        return [doCall]

    def getUnittestExternInclude(self)->list:
        """!
        @brief Return static specific include and external function definition strings
        @return list of strings - static specific #if, #include, external function and #endif code
        """
        incBlock = []
        incBlock.append("#if "+self.defStaticString+"\n")
        incBlock.append(self.genExternDefinition())
        incBlock.append("#endif // "+self.defStaticString+"\n")
        return incBlock

    def getUnittestFileName(self)->tuple:
        """!
        @return tuple(str,str) - Unit test cpp file name, Test name
        """
        return "LocalLanguageSelect_Static_test.cpp", "LocalLanguageSelect_Static_te"
