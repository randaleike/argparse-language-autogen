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

from .common.doxygen_gen_tools import CDoxyCommentGenerator
from .string_class_tools import BaseCppClassGenerator

class StaticLangSelectFunctionGenerator(BaseCppClassGenerator):
    """!
    Methods for compile switch determined language select function generation
    """
    def __init__(self, jsonLangData, functionName = "getParserStringListInterface_Static", dynamicCompileSwitch="DYNAMIC_INTERNATIONALIZATION"):
        """!
        @brief StaticLangSelectFunctionGenerator constructor
        @param jsonLangData {string} JSON language description list file name
        @param functionName {string} Function name to be used for generation
        @param dynamicCompileSwitch {string} Dynamic international compile switch name
        """
        super().__init__()
        self.selectFunctionName = functionName
        self.defStaticString = "!defined("+dynamicCompileSwitch+")"
        self.langJsonData = jsonLangData
        self.doxyCommentGen = CDoxyCommentGenerator()

    def getFunctionName(self):
        return self.selectFunctionName

    def getOsDefine(self):
        return None

    def getOsDynamicDefine(self):
        return self.defStaticString

    def genFunctionDefine(self):
        """!
        @brief Get the function declaration string for the given name
        @return string list - Function comment block and declaration start
        """
        return(self._genFunctionDefine(self.selectFunctionName,
                                       "Determine the correct local language class from the compile switch setting",
                                       []))

    def genFunctionEnd(self):
        """!
        @brief Get the function declaration string for the given name
        @return string - Function close with comment
        """
        return self.endFunction(self.selectFunctionName)

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
            functionBody.append(bodyIndent+self.genMakePtrReturnStatement(langName))

        # Add the final #else case
        functionBody.append("  #else //undefined language compile switch, use default\n")
        functionBody.append(bodyIndent+"#error one of the language compile switches must be defined\n")
        functionBody.append("  #endif //end of language #if/#elifcompile switch chain\n")

        # Complete the function
        functionBody.append(self.genFunctionEnd())
        functionBody.append("#endif // "+self.defStaticString+"\n")
        outfile.writelines(functionBody)

    def genReturnFunctionCall(self, indent = 4):
        """!
        @brief Generate the call code for the linux dynamic lang selection function
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        doCall = indentText+"return "+self.selectFunctionName+"();\n"
        return [doCall]

    def genExternDefinition(self):
        """!
        @brief Return the external function definition
        @return string - External function definition line
        """
        externDef = "extern "
        externDef += self.returnType
        externDef += " "
        externDef += self.selectFunctionName
        externDef += "();\n"
        return externDef

    def genUnitTest(self, getIsoMethod, outfile):
        """!
        @brief Generate all unit tests for the selection function

        @param getIsoMethod {string} Name of the ParserStringListInterface return ISO code method
        @param outfile {file} File to output the function to
        """
        # Generate block start code
        blockStart = []
        blockStart.append("#if "+self.defStaticString+"\n")
        blockStart.append(self.genExternDefinition())
        outfile.writelines(blockStart)

        # Generate the testgenDoxyMethodComment
        testBlockName = "StaticSelectFunction"
        bodyIndent = "".rjust(4, " ")
        breifDesc = "Test "+self.selectFunctionName+" selection case"
        testBody = self.doxyCommentGen.genDoxyMethodComment(breifDesc, [])

        testVar = "testVar"
        testVarDecl = self.returnType+" "+testVar
        testVarTest = testVar+"."+getIsoMethod+"().c_str()"
        testBody.append("TEST("+testBlockName+", CompileSwitchedValue)\n")
        testBody.append("{\n")
        testBody.append(bodyIndent+"// Generate the test language string object\n")
        testBody.append(bodyIndent+testVarDecl+" = "+self.selectFunctionName+"();\n")
        testBody.append("\n") # whitespace for readability

        firstLoop = True
        for langName in self.langJsonData.getLanguageList():
            if firstLoop:
                testBody.append("  #if defined("+self.langJsonData.getLanguageCompileSwitchData(langName)+")\n")
                firstLoop = False
            else:
                testBody.append("  #elif defined("+self.langJsonData.getLanguageCompileSwitchData(langName)+")\n")

            testBody.append(bodyIndent+"EXPECT_STREQ(\""+self.langJsonData.getLanguageIsoCodeData(langName)+"\", "+testVarTest+";\n")

        # Add the final #else case
        testBody.append("  #else //undefined language compile switch, use default\n")
        testBody.append(bodyIndent+"#error One compile switch language must be defined!\n")
        testBody.append("  #endif //end of language #if/#elifcompile switch chain\n")

        # Complete the function
        testBody.append("}\n")
        outfile.writelines(testBody)

        # Generate block end code
        outfile.writelines(["#endif // "+self.defStaticString+"\n"])

    def genUnitTestFunctionCall(self, checkVarName, indent = 4):
        """!
        @brief Generate the call code for the linux dynamic lang selection unit test
        @param checkVarName {string} Unit test expected variable name
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        doCall = indentText+self.returnType+" "+checkVarName+" = "+self.selectFunctionName+"();\n"
        return [doCall]

    def getUnittestExternInclude(self):
        incBlock = []
        incBlock.append("#if "+self.defStaticString+"\n")
        incBlock.append(self.genExternDefinition())
        incBlock.append("#endif // "+self.defStaticString+"\n")
        return incBlock

    def getUnittestFileName(self):
        """!
        @return string Unit test cpp file name
        """
        return "LocalLanguageSelect_Static_test.cpp"
