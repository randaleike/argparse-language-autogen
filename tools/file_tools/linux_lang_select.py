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
from .json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from .common.doxygen_gen_tools import CDoxyCommentGenerator
from .string_class_tools import BaseStringClassGenerator

class LinuxLangSelectFunctionGenerator(BaseStringClassGenerator):
    """!
    Methods for Linux language select function generation
    """
    def __init__(self, jsonLangData:LanguageDescriptionList, owner:str|None = None, eulaName:str|None = None, baseClassName:str = "BaseClass",
                 dynamicCompileSwitch:str = "DYNAMIC_INTERNATIONALIZATION"):
        """!
        @brief LinuxLangSelectFunctionGenerator constructor
        @param jsonLangData {string} JSON language description list file name
        @param owner {string|None} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string|None} Name of the EULA to pass down to the BaseStringClassGenerator parent
        @param baseClassName {string} Name of the base class for name generation
        @param dynnamicCompileSwitch {string} Dynamic compile switch for #if generation
        """
        super().__init__(owner, eulaName, baseClassName, dynamicCompileSwitch)
        self.selectFunctionName = "get"+baseClassName+"_Linux"

        self.paramDictList = [ParamRetDict.buildParamDict("langId", "const char*", "Current LANG value from the program environment")]
        self.defOsString = "(defined(__linux__) || defined(__unix__))"
        self.langJsonData = jsonLangData
        self.doxyCommentGen = CDoxyCommentGenerator()

    def getFunctionName(self)->str:
        return self.selectFunctionName

    def getOsDefine(self)->str:
        return self.defOsString

    def genFunctionDefine(self)->list:
        """!
        @brief Get the function declaration string for the given name
        @return string list - Function comment block and declaration start
        """
        codeList = self._defineFunctionWithDecorations(self.selectFunctionName,
                                                       "Determine the correct local language class from the input LANG environment setting",
                                                       self.paramDictList,
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
        functionBody.append("#if "+self.defOsString+"\n")
        functionBody.append(self._genInclude("<cstdlib>"))
        functionBody.append(self._genInclude("<regex>"))
        functionBody.append("\n")  # whitespace for readability

        # Generate function doxygen comment and start
        functionBody.extend(self.genFunctionDefine())

        # Start function body generation
        paramName = ParamRetDict.getParamName(self.paramDictList[0])
        bodyIndent = "    "
        functionBody.append(bodyIndent+"// Check for valid input\n")
        functionBody.append(bodyIndent+"if (nullptr != "+paramName+")\n")
        functionBody.append(bodyIndent+"{\n")

        # Generate if/else if chain for each language in the dictionary
        if1BodyIndent = bodyIndent+"".rjust(4, " ")
        functionBody.append(if1BodyIndent+"// Break the string into its components\n")
        functionBody.append(if1BodyIndent+"std::cmatch searchMatch;\n")
        functionBody.append(if1BodyIndent+"std::regex searchRegex(\"^([a-z]{2})_([A-Z]{2})\\\\.(UTF-[0-9]{1,2})\");\n")
        functionBody.append(if1BodyIndent+"bool matched = std::regex_match("+paramName+", searchMatch, searchRegex);\n")
        functionBody.append("\n")  # whitespace for readability
        functionBody.append(if1BodyIndent+"// Determine the language\n")

        if2BodyIndent = if1BodyIndent+"".rjust(4, " ")
        firstCheck = True
        for langName in self.langJsonData.getLanguageList():
            langCode, regionList = self.langJsonData.getLanguageLANGData(langName)
            ifline = ""
            if firstCheck:
                ifline += "if (matched && "
                firstCheck = False
            else:
                ifline += "else if (matched && "

            ifline += "(searchMatch[1].str() == \""
            ifline += langCode
            ifline += "\"))\n"

            functionBody.append(if1BodyIndent+ifline)
            functionBody.append(if1BodyIndent+"{\n")
            functionBody.append(if2BodyIndent+self._genMakePtrReturnStatement(langName))
            functionBody.append(if1BodyIndent+"}\n")

        # Add the final else (unknown language) case
        defaultLang, defaultIsoCode = self.langJsonData.getDefaultData()
        functionBody.append(if1BodyIndent+"else //unknown language code, use default language\n")
        functionBody.append(if1BodyIndent+"{\n")
        functionBody.append(if2BodyIndent+self._genMakePtrReturnStatement(defaultLang))
        functionBody.append(if1BodyIndent+"}\n")

        # Add the else if nullptr case
        functionBody.append(bodyIndent+"}\n")
        functionBody.append(bodyIndent+"else // null pointer input, use default language\n")
        functionBody.append(bodyIndent+"{\n")
        functionBody.append(if1BodyIndent+self._genMakePtrReturnStatement(defaultLang))
        functionBody.append(bodyIndent+"} // end of if(nullptr != "+paramName+")\n")

        # Complete the function
        functionBody.append(self.genFunctionEnd())
        functionBody.append("#endif // "+self.defOsString+"\n")
        outfile.writelines(functionBody)

    def genReturnFunctionCall(self, indent:int = 4)->list:
        """!
        @brief Generate the call code for the linux dynamic lang selection function
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        localVarName = "langId"

        getParam =  indentText
        getParam += ParamRetDict.getParamType(self.paramDictList[0])
        getParam += " "
        getParam += localVarName
        getParam += "= getenv(\"LANG\");\n"

        doCall = indentText
        doCall += "return "
        doCall += self.selectFunctionName
        doCall += "("
        doCall += localVarName
        doCall += ");\n"

        return [getParam, doCall]

    def _genUnitTestTest(self, testName:str, linuxEnvString:str, expectedIso:str, getIsoMethod:str)->list:
        """!
        @brief Generate single selection function unit test instance

        @param testName {string} Name of the test
        @param linuxEnvString {string} Environment string value to send to the select function
        @param expectedIso {string} Expected ISO return code for the test variable
        @param getIsoMethod {string} Name of the ParserStringListInterface return ISO code method

        @return list of strings - Output C code
        """
        testBlockName = "LinuxSelectFunction"
        bodyIndent = "".rjust(4, " ")
        breifDesc = "Test "+self.selectFunctionName+" "+linuxEnvString+" selection case"
        testBody = self.doxyCommentGen.genDoxyMethodComment(breifDesc, [])

        testVar = "testVar"
        testVarDecl = self.baseIntfRetPtrType+" "+testVar
        testVarTest = testVar+"->"+getIsoMethod+"().c_str()"
        testBody.append("TEST("+testBlockName+", "+testName+")\n")
        testBody.append("{\n")
        testBody.append(bodyIndent+"// Generate the test language string object\n")
        testBody.append(bodyIndent+"std::string testLangCode = \""+linuxEnvString+"\";\n")
        testBody.append(bodyIndent+testVarDecl+" = "+self.selectFunctionName+"(testLangCode.c_str());\n")
        testBody.append(bodyIndent+"EXPECT_STREQ(\""+expectedIso+"\", "+testVarTest+");\n")
        testBody.append("}\n")
        return testBody

    def genExternDefinition(self)->str:
        """!
        @brief Return the external function definition
        @return string - External function definition line
        """
        externDef = "extern "
        externDef += self.baseIntfRetPtrType
        externDef += " "
        externDef += self.selectFunctionName
        externDef += "("
        externDef += ParamRetDict.getParamType(self.paramDictList[0])
        externDef += " "
        externDef += ParamRetDict.getParamName(self.paramDictList[0])
        externDef += ");\n"
        return externDef

    def genUnitTest(self, getIsoMethod:str, outfile):
        """!
        @brief Generate all unit tests for the selection function

        @param getIsoMethod {string} Name of the ParserStringListInterface return ISO code method
        @param outfile {file} File to output the function to
        """
        # Generate block start code
        blockStart = []
        blockStart.append("#if "+self.defOsString+"\n")
        blockStart.append("\n") # white space for readability
        blockStart.append(self._genInclude("<cstdlib>"))
        blockStart.append(self.genExternDefinition())
        blockStart.append("\n") # white space for readability
        outfile.writelines(blockStart)

        # Generate the tests
        for langName in self.langJsonData.getLanguageList():
            langCode, regionList = self.langJsonData.getLanguageLANGData(langName)
            for region in regionList:
                # Generate test for each region of known language
                linuxEnvString = langCode+"_"+region+".UTF-8"
                testName = langName.capitalize()+"_"+region+"_Selection"
                testBody = self._genUnitTestTest(testName,
                                                 linuxEnvString,
                                                 self.langJsonData.getLanguageIsoCodeData(langName),
                                                 getIsoMethod)
                testBody.append("\n") # whitespace for readability
                outfile.writelines(testBody)

            # Generate test for unknown region of known language
            unknownRegionTestName =langName.capitalize()+"_unknownRegion_Selection"
            unknownRegionEnv = langCode+"_XX.UTF-8"
            unknownRegionBody = self._genUnitTestTest(unknownRegionTestName,
                                                      unknownRegionEnv,
                                                      self.langJsonData.getLanguageIsoCodeData(langName),
                                                      getIsoMethod)
            unknownRegionBody.append("\n") # whitespace for readability
            outfile.writelines(unknownRegionBody)

        # Generate test for unknown region of unknown language and expect default
        defaultLang, defaultIsoCode = self.langJsonData.getDefaultData()
        unknownLangBody = self._genUnitTestTest("UnknownLanguageDefaultSelection",
                                                "xx_XX.UTF-8",
                                                defaultIsoCode,
                                                getIsoMethod)
        outfile.writelines(unknownLangBody)

        # Generate block end code
        outfile.writelines(["#endif // "+self.defOsString+"\n"])

    def genUnitTestFunctionCall(self, checkVarName:str, indent:int = 4)->list:
        """!
        @brief Generate the call code for the linux dynamic lang selection unit test
        @param checkVarName {string} Unit test expected variable name
        @param indent {number} Code indentation spaces
        @return list of strings Formatted code lines
        """
        indentText = "".rjust(indent, " ")
        localVarName = "langId"

        getParam =  indentText
        getParam += ParamRetDict.getParamType(self.paramDictList[0])
        getParam += " "
        getParam += localVarName
        getParam += " = getenv(\"LANG\");\n"

        doCall = indentText
        doCall += self.baseIntfRetPtrType
        doCall += " "
        doCall += checkVarName
        doCall += " = "
        doCall += self.selectFunctionName
        doCall += "("
        doCall += localVarName
        doCall += ");\n"

        return [getParam, doCall]

    def getUnittestExternInclude(self)->list:
        """!
        @brief Return linux specific include and external function definition strings
        @return list of strings - linux specific #if, #include, external function and #endif code
        """
        incBlock = []
        incBlock.append("#if "+self.defOsString+"\n")
        incBlock.append(self._genInclude("<cstdlib>"))
        incBlock.append(self.genExternDefinition())
        incBlock.append("#endif // "+self.defOsString+"\n")
        return incBlock

    def getUnittestFileName(self)->tuple:
        """!
        @return tuple(str,str) - Unit test cpp file name, Test name
        """
        return "LocalLanguageSelect_Linux_test.cpp", "LocalLanguageSelect_Linux_test"
