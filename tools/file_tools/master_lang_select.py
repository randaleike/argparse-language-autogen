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
from .string_class_tools import BaseStringClassGenerator

class MasterSelectFunctionGenerator(BaseStringClassGenerator):
    """!
    Methods for master language select function generation
    """
    def __init__(self, owner:str|None = None, eulaName:str|None = None, baseClassName:str = "BaseClass",
                 methodName:str = "getLocalParserStringListInterface",
                 dynamicCompileSwitch:str = "DYNAMIC_INTERNATIONALIZATION"):
        """!
        @brief MasterSelectFunctionGenerator constructor
        @param owner {string|None} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string|None} Name of the EULA to pass down to the BaseStringClassGenerator parent
        @param baseClassName {string} Name of the base class for name generation
        @param methodName {string} Function name to be used for generation
        @param dynnamicCompileSwitch {string} Dynamic compile switch for #if generation
        """
        super().__init__(owner, eulaName, baseClassName, dynamicCompileSwitch)
        self.selectFunctionName = baseClassName+"::"+methodName
        self.selectBaseFunctionName = methodName

        self.briefDesc = "Determine the OS use OS specific functions to determine the correct local language" \
                         "based on the OS specific local language setting and return the correct class object"
        self.doxyCommentGen = CDoxyCommentGenerator()

    def getFunctionName(self)->str:
        return self.selectFunctionName

    def getFunctionDesc(self)->tuple:
        """!
        @brief Generate a function declatation text block with doxygen comment
        @return tuple - Function (name, description, return dictionary, param list)
        """
        return self.selectBaseFunctionName, self.briefDesc, self.baseIntfRetPtrDict, []

    def genFunctionDefine(self)->list:
        """!
        @brief Get the function declaration string for the given name
        @return string list - Function comment block and declaration start
        """
        codeList = self._defineFunctionWithDecorations(self.selectFunctionName, self.briefDesc, [], self.baseIntfRetPtrDict)
        codeList.append("{\n")
        return codeList

    def genFunctionEnd(self)->str:
        """!
        @brief Get the function declaration string for the given name
        @return string - Function close with comment
        """
        return self._endFunction(self.selectFunctionName)

    def genFunction(self, outfile, osLangSelectors):
        """!
        @brief Generate the function body text
        @param outfile {file} File to output the function to
        @param osLangSelectors {list} List of OS language selector function generation objects
        """
        # Generate function doxygen comment and start
        functionBody = []
        functionBody.extend(self.genFunctionDefine())
        bodyIndent = 4
        bodyPrefix = "".rjust(bodyIndent, ' ')

        # Generate OS calls
        firstOs = True
        for osSelector in osLangSelectors:
            if firstOs:
                functionBody.append("#if "+osSelector.getOsDefine()+"\n")
                firstOs = False
            else:
                functionBody.append("#elif "+osSelector.getOsDefine()+"\n")
            functionBody.extend(osSelector.genReturnFunctionCall(bodyIndent))

        # Add the #else case
        functionBody.append("#else // not defined os\n")
        functionBody.append(bodyPrefix+"#error No language generation method defined for this OS\n")

        # Complete the function
        functionBody.append("#endif // defined os\n")
        functionBody.append(self.genFunctionEnd())
        outfile.writelines(functionBody)

    def genReturnFunctionCall(self, indent:int = 4)->list:
        """!
        @brief Generate the call code for the linux dynamic lang selection function
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        doCall = "return "+self.selectFunctionName+"();\n"
        return [doCall.rjust(indent, " ")]

    def genUnitTest(self, getIsoMethod:str, outfile, osLangSelectors):
        """!
        @brief Generate all unit tests for the selection function

        @param getIsoMethod {string} Name of the ParserStringListInterface return ISO code method
        @param outfile {file} File to output the function to
        @param osLangSelectors {list} List of OS language selector function generation objects
        """
        testBody = []

        # generate the externals
        for osSelector in osLangSelectors:
            testBody.extend(osSelector.getUnittestExternInclude())
        testBody.append("\n") # whitespace for readability

        # Generate the test
        testBlockName = "SelectFunction"
        bodyIndentIndex = 4
        bodyIndent = "".rjust(bodyIndentIndex, " ")
        breifDesc = "Test "+self.selectFunctionName+" selection case"
        testBody.extend(self.doxyCommentGen.genDoxyMethodComment(breifDesc, []))

        testVar = "testVar"
        testVarDecl = self.baseIntfRetPtrType+" "+testVar
        testBody.append("TEST("+testBlockName+", TestLocalSelectMethod)\n")
        testBody.append("{\n")

        # Generate OS calls
        firstOs = True
        expectedParser = "localStringParser"
        for osSelector in osLangSelectors:
            if firstOs:
                testBody.append("#if "+osSelector.getOsDefine()+"\n")
                firstOs = False
            else:
                testBody.append("#elif "+osSelector.getOsDefine()+"\n")
            testBody.append(bodyIndent+"// Get the expected value\n")
            testBody.extend(osSelector.genUnitTestFunctionCall(expectedParser, bodyIndentIndex))

        # Add the #else case
        testBody.append("#else // not defined os\n")
        testBody.append(bodyIndent+"#error No language generation defined for this OS\n")

        # Complete the function
        testBody.append("#endif // defined os\n")
        getExpectedVal = expectedParser+"->"+getIsoMethod+"().c_str()"
        testVarTest = testVar+"->"+getIsoMethod+"().c_str()"
        testBody.append("\n") # whitespace for readability

        testBody.append(bodyIndent+"// Generate the test language string object\n")
        testBody.append(bodyIndent+testVarDecl+" = "+self.selectFunctionName+"();\n")
        testBody.append(bodyIndent+"EXPECT_STREQ("+getExpectedVal+", "+testVarTest+");\n")
        testBody.append(self.genFunctionEnd())
        outfile.writelines(testBody)
