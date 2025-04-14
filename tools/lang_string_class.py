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

import os

from jsonLanguageDescriptionList import LanguageDescriptionList
from jsonStringClassDescription import StringClassDescription

from file_tools.common.param_return_tools import ParamRetDict

from file_tools.string_name_generator import StringClassNameGen
from file_tools.string_class_tools import BaseStringClassGenerator

class GenerateLangFiles(BaseStringClassGenerator):
    def __init__(self, jsonLangFileName, jsonStringsFilename, owner = None, eulaName = None):
        """!
        @brief GenerateLangFiles constructor

        @param jsonLangFileName {string} Path/Filename of the JSON language list file to use
        @param jsonStringsFilename {string} Path/Filename of the JSON property/translate string file to use
        @param owner {string} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string} EULA text to use in the header message or None to default MIT Open
        """
        super().__init__(owner, eulaName)
        self.jsonLangData = LanguageDescriptionList(jsonLangFileName)
        self.jsonStringsData = StringClassDescription(jsonStringsFilename)
        self.nameSpaceName = StringClassNameGen.getNamespaceName()

    def _genPropertyCode(self, langName, propertyName, propertyReturn, isText):
        """!
        @brief Generate property function code
        @param langName {string} Language name
        @param propertyName {string} Language property name
        @param propertyReturn {dictionary} Property method return dictionary
        @return list of strings - Inline code
        """
        returnType = ParamRetDict.getReturnType(propertyReturn)
        codeTxt = []
        if ParamRetDict.isReturnList(propertyReturn):
            # List case
            dataList = self.jsonLangData.getLanguagePropertyData(langName, propertyName)
            codeTxt.append(returnType+" returnData;")

            # Determine data type
            for dataItem in dataList:
                if isText:
                    codeTxt.append(self.getAddStringListStatment("returnData", dataItem))
                else:
                    codeTxt.append(self.getAddValueListStatment("returnData", dataItem))
            codeTxt.append("return returnData;")
        else:
            # Single item case
            dataItem = self.jsonLangData.getLanguagePropertyData(langName, propertyName)

            # Determine data type
            if isText:
                codeTxt.append("return (\""+dataItem+"\");")
            else:
                codeTxt.append("return ("+dataItem+");")

        return codeTxt

    def _writeIncPropertyMethods(self, hFile, langName):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        @param langName {string} Language name or None this is for the base file
        """
        # Add the property fetch methods
        postfix = "final"

        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)

            # Translate the return type and input params
            xlatedRetDict, isText = self.xlateReturnDict(propertyReturn)
            xlatedParamList = self.xlateParamList(propertyParams)

            # Output final declaration
            self._writeMethod(hFile, propertyMethod, propertyDesc, xlatedParamList, xlatedRetDict, None, postfix)

    def _writeSrcPropertyMethods(self, cppFile, langName, className):
        """!
        @brief Write the property method sourc file definitios

        @param hFile {File} File to write the data to
        @param langName {string} Language name or None this is for the base file
        @param className {string} Class name decoration
        """
        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)

            # Translate the return type
            xlatedRetDict, isText = self.xlateReturnDict(propertyReturn)
            xlatedParamList = self.xlateParamList(propertyParams)
            if len(xlatedParamList) == 0:
                postfix = "const"
            else:
                postfix = None

            # Output final declaration
            methodDef = self.defineFunctionWithDecorations(className+"::"+propertyMethod,
                                                           propertyDesc,
                                                           xlatedParamList,
                                                           xlatedRetDict,
                                                           False,
                                                           None,
                                                           postfix)
            cppFile.writelines(methodDef)

            # Get the language data replacements
            codeText = self._genPropertyCode(langName, propertyName, xlatedRetDict, isText)

            # Output code body
            if len(codeText) == 1:
                cppFile.writelines(["{"+codeText[0]+"}\n"])
            else:
                bodyIndent = "".rjust(self.functionIndent, ' ')
                cppFile.writelines(["{\n"])
                for line in codeText:
                    cppFile.writelines([bodyIndent+line+"\n"])
                cppFile.writelines(["}\n"])

    def _translateString(self, baseLanguage, baseText, targetLang):
        """!
        @brief Translate the baseText string into the target language from the base language
        @param baseLanguage {string} Google translate language code of the baseText string
        @param baseText {string} String to translate and output
        @param targetLang {string} Google translate language code for the translated baseText string
        @return string - Translated string
        """
        if baseLanguage == targetLang:
            return baseText
        else:
            #client = translate.Client(target_langage=targetLang,credentials=)
            return baseText

    def _writeIncTranslateMethods(self, hFile, langName):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        @param langName {string} Language name or None this is for the base file
        """
        # Add the property fetch methods
        postfixFinal = "final"

        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)

            # Output the function
            self._writeMethod(hFile, translateMethodName, transDesc, transParams, transReturn, None, postfixFinal)

    def _genTranslateCode(self, streamDescList):
        """!
        @brief Generate the string output code
        @param inlineStreamDescList {tuple list} Stream output tuple list
        @return string - Inline code
        """
        streamString = StringClassNameGen.getParserStrStreamType()+" parserstr;  parserstr"
        for outputDesc in streamDescList:
            if StringClassNameGen.isParsedTextType(outputDesc):
                streamString += ' << "'
                streamString += StringClassNameGen.getParsedStrData(outputDesc)
                streamString += '"'
            if StringClassNameGen.isParsedParamType(outputDesc):
                streamString += ' << '
                streamString += StringClassNameGen.getParsedStrData(outputDesc)
        streamString += "; return parserstr.str();"
        return streamString

    def _writeSrcTranslateMethods(self, cppFile, langName, className):
        """!
        @brief Write the property method definitions

        @param cppFile {File} File to write the data to
        @param langName {string} Language name or None this is for the base file
        @param className {string} Class name decoration
        """
        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)

            # Translate the return type
            xlatedRetDict, isText = self.xlateReturnDict(transReturn)
            xlatedParamList = self.xlateParamList(transParams)
            if len(xlatedParamList) == 0:
                postfix = "const"
            else:
                postfix = None

            # Output final declaration
            methodDef = self.defineFunctionWithDecorations(className+"::"+translateMethodName,
                                                           transDesc,
                                                           xlatedParamList,
                                                           xlatedRetDict,
                                                           False,
                                                           None,
                                                           postfix,
                                                           None)
            cppFile.writelines(methodDef)

            # Get the language generation string if needed
            targetLang = self.jsonLangData.getLanguageGoogleCodeData(langName)

            # Get the language data replacements
            streamDesc = self.jsonStringsData.getTranlateMethodTextData(translateMethodName, targetLang)
            codeText = self._genTranslateCode(streamDesc)

            # Output code body
            cppFile.writelines(["{"+codeText+"}\n"])

    def _writeHFile(self, hFile, langName):
        """!
        @brief Write the language specific include file

        @param hFile {File} File to write the data to
        @param langName {string} - Language name
        """
        # Write the common header datajsonStringsDef
        hFile.writelines(self._generateFileHeader())
        hFile.writelines(["\n"]) # whitespace for readability

        includeList = ["<cstdio>",
                       "<cstring>",
                       StringClassNameGen.getBaseClassName()+".h",]
        hFile.writelines(self.genIncludeBlock(includeList))
        hFile.writelines(["\n"]) # whitespace for readability

        # Set the class name
        className = StringClassNameGen.getLangClassName(langName)
        hFile.writelines(["using namespace "+self.nameSpaceName+";\n"])

        # Start class definition
        hFile.writelines(self.genClassOpen(className,
                                            "Language specific parser error/help string generation interface",
                                            "public "+StringClassNameGen.getBaseClassName(),
                                            "final"))
        hFile.writelines(["    public:\n"])

        # Add default Constructor/destructor definitions
        hFile.writelines(self.genClassDefaultConstructorDestructor(className, self.declareIndent, False, True))

        # Add the property fetch methods
        self._writeIncPropertyMethods(hFile, langName)
        hFile.writelines(["\n"]) # whitespace for readability

        # Add the string generation methods
        self._writeIncTranslateMethods(hFile, langName)

        # Close the class
        hFile.writelines(self.genClassClose(className))

    def _writeCppFile(self, cppFile, langName):
        """!
        @brief Write the language specific source file

        @param cppFile {File} File to write the data to
        @param langName {string} - Language name
        """
        # Write the common header data
        cppFile.writelines(self._generateFileHeader())
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the common includes
        includeFileList = ["<sstream>",
                           self._generateHFileName(),
                           self._generateHFileName(langName)]
        cppFile.writelines(self.genIncludeBlock(includeFileList))

        className = StringClassNameGen.getLangClassName(langName)
        cppFile.writelines(["using namespace "+self.nameSpaceName+";\n"])
        cppFile.writelines(["using "+StringClassNameGen.getParserStrStreamType()+" = std::stringstream;\n", "\n"])

        # Add doxygen group start
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateCppFileName(), self.groupName, self.groupDesc))
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the property fetch methods
        self._writeSrcPropertyMethods(cppFile, langName, className)
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the string generation methods
        self._writeSrcTranslateMethods(cppFile, langName, className)

        # Complete the doxygen group
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def _genUnitPropertyParamInput(self, xlatedParamType):
        if xlatedParamType == self.xlateMatrix['string']:
            return "\"test\""
        elif xlatedParamType == self.xlateMatrix['size']:
            return "2"
        elif xlatedParamType == self.xlateMatrix['integer']:
            return "-1"
        elif xlatedParamType == self.xlateMatrix['unsigned']:
            return "1"
        elif xlatedParamType == self.xlateMatrix['LANGID']:
            return "10"
        else:
            return "5"

    def _generatePropertyUnittest(self, propertyMethod, langName):
        """!
        @brief Generate the unit test for the input property method
        @param propertyMethod {string} Property function name
        @param langName {string} Language name
        @return list of strings - Test code to output
        """
        codeText = []
        propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)
        unitTestSectionName = StringClassNameGen.getLangClassName(langName)
        bodyIndent = "".rjust(4, ' ')

        # Translate the return type
        xlatedRetDict, isRetText = self.xlateReturnDict(propertyReturn)
        codeText.append("TEST("+unitTestSectionName+", fetch"+propertyMethod+")\n")
        codeText.append("{\n")
        codeText.append(bodyIndent+StringClassNameGen.getLangClassName(langName)+" testvar;\n")

        # Build the property function call
        fetchCode = ParamRetDict.getReturnType(xlatedRetDict)
        fetchCode += " output = testvar."
        fetchCode += propertyMethod
        fetchCode += "("
        paramPrefix = ""
        for param in propertyParams:
            paramType = ParamRetDict.getParamType(param)
            xlatedParamType, isText = self.xlateGenericType(paramType, False)
            fetchCode += paramPrefix
            fetchCode += self._genUnitPropertyParamInput(xlatedParamType)
            paramPrefix = ", "
        fetchCode += ");\n"
        codeText.append(bodyIndent+fetchCode)

        # Build the test assertion
        if isRetText:
            if ParamRetDict.isReturnList(xlatedRetDict):
                codeText.append(bodyIndent+"for (auto const &item : output)\n")
                codeText.append(bodyIndent+"{\n")
                forBodyIndent = bodyIndent+"".rjust(4, ' ')
                for item in self.jsonLangData.getLanguagePropertyData(langName, propertyName):
                    assertText = "EXPECT_STREQ("
                    assertText += "\""
                    assertText += item
                    assertText += "\", item.c_str());\n"
                    codeText.append(forBodyIndent+assertText)
                codeText.append(bodyIndent+"}\n")
            else:
                assertText = "EXPECT_STREQ("
                assertText += "\""
                assertText += self.jsonLangData.getLanguagePropertyData(langName, propertyName)
                assertText += "\", output.c_str());\n"
                codeText.append(bodyIndent+assertText)
        else:
            if ParamRetDict.isReturnList(xlatedRetDict):
                codeText.append(bodyIndent+"for (auto const &item : output)\n")
                codeText.append(bodyIndent+"{\n")
                forBodyIndent = bodyIndent+"".rjust(4, ' ')
                for item in self.jsonLangData.getLanguagePropertyData(langName, propertyName):
                    assertText = "EXPECT_EQ("
                    assertText += item
                    assertText += ", item);\n"
                    codeText.append(forBodyIndent+assertText)
                codeText.append(bodyIndent+"}\n")
            else:
                assertText = "EXPECT_EQ("
                assertText += self.jsonLangData.getLanguagePropertyData(langName, propertyName)
                assertText += ", output);\n"
                codeText.append(bodyIndent+assertText)
        codeText.append("}\n")
        return codeText

    def _genUnitTransParamInput(self, paramName, isInput):
        if paramName == "keyString":
            if isInput:
                return "\"-test\""
            else:
                return "-test"
        if paramName == "envString":
            if isInput:
                return "\"envtest\""
            else:
                return "envtest"
        elif paramName == "nargs":
            return "3"
        elif paramName == "nargsExpected":
            return "2"
        elif paramName == "nargsFound":
            return "1"
        elif paramName == "vargRange":
            if isInput:
                return "\"<-100:100>\""
            else:
                return "<-100:100>"
        elif paramName == "vargType":
            if isInput:
                return "\"integer\""
            else:
                return "integer"
        else:
            return "5"

    def _generateTranslateUnittest(self, translateMethodName, langName):
        """!
        @brief Generate the unit test for the input property method
        @param propertyMethod {string} Property function name
        @param langName {string} Language name
        @return list of strings - Test code to output
        """
        codeText = []
        transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)
        unitTestSectionName = StringClassNameGen.getLangClassName(langName)
        bodyIndent = "".rjust(4, ' ')

        # Translate the return type
        xlatedRetDict, isRetText = self.xlateReturnDict(transReturn)
        codeText.append("TEST("+unitTestSectionName+", print"+translateMethodName+")\n")
        codeText.append("{\n")
        codeText.append(bodyIndent+StringClassNameGen.getLangClassName(langName)+" testvar;\n")

        # Build the property function call
        fetchCode = ParamRetDict.getReturnType(xlatedRetDict)
        fetchCode += " output = testvar."
        fetchCode += translateMethodName
        fetchCode += "("
        paramPrefix = ""
        for param in transParams:
            paramType = ParamRetDict.getParamType(param)
            xlatedParamType, isText = self.xlateGenericType(paramType, False)
            fetchCode += paramPrefix
            fetchCode += self._genUnitTransParamInput(ParamRetDict.getParamName(param), True)
            paramPrefix = ", "
        fetchCode += ");\n"
        codeText.append(bodyIndent+fetchCode)

        # Build the expected string
        targetLang = self.jsonLangData.getLanguageGoogleCodeData(langName)
        expectedString = ""
        stringData = self.jsonStringsData.getTranlateMethodTextData(translateMethodName, targetLang)
        for strDescTuple in stringData:
            if StringClassNameGen.isParsedTextType(strDescTuple):
                expectedString += StringClassNameGen.getParsedStrData(strDescTuple)
            elif StringClassNameGen.isParsedParamType(strDescTuple):
                expectedString += self._genUnitTransParamInput(StringClassNameGen.getParsedStrData(strDescTuple), False)
            else:
                print("Error: Unknown StringClassNameGen parsed string list type "+str(strDescTuple[0]))

        # Build the assertion test
        assertText = "EXPECT_STREQ("
        assertText += "\""
        assertText += expectedString
        assertText += "\", output.c_str());\n"
        codeText.append(bodyIndent+assertText)
        codeText.append("}\n")
        return codeText

    def _writeUnittestFile(self, testFile, langName):
        """!
        @brief Write the OS language selection CPP file

        @param testFile {File} File to write the data to
        @param langName {string} - Language name
        """
        # Write the common header datajsonStringsDef
        testFile.writelines(self._generateFileHeader())
        testFile.writelines(["\n"]) # whitespace for readability

        # Add the common includes
        includeFileList = ["<cstdio>",
                           "<cstring>",
                           "<sstream>",
                           "<gtest/gtest.h>",
                           self._generateHFileName(),
                           self._generateHFileName(langName)]
        testFile.writelines(self.genIncludeBlock(includeFileList))

        # Add doxygen group start
        testFile.writelines(["\n"]) # whitespace for readability
        testFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateUnittestFileName(),
                                                                self.groupName+langName+'unittest',
                                                                self.groupDesc+' '+langName+' unit test'))

        testFile.writelines(["\n"]) # whitespace for readability

        # Set the class name
        className = StringClassNameGen.getLangClassName(langName)
        testFile.writelines(["using namespace "+self.nameSpaceName+";\n"])
        testFile.writelines(["using "+StringClassNameGen.getParserStrStreamType()+" = std::stringstream;\n", "\n"])
        testFile.writelines(["// NOLINTBEGIN\n"])

        # Add the property fetch method tests
        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyTestCode = self._generatePropertyUnittest(propertyMethod, langName)
            testFile.writelines(propertyTestCode)
            testFile.writelines(["\n"]) # whitespace for readability

        # Add the string generation method tests
        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            translateTestCode = self._generateTranslateUnittest(translateMethodName, langName)
            testFile.writelines(translateTestCode)
            testFile.writelines(["\n"]) # whitespace for readability

        # Add the test main
        testFile.writelines(["// NOLINTEND\n"])
        testFile.writelines(["// Execute the tests\n"])
        testFile.writelines(["int main(int argc, char **argv)\n"])
        testFile.writelines(["{\n"])
        testFile.writelines(["    ::testing::InitGoogleTest(&argc, argv);\n"])
        testFile.writelines(["    return RUN_ALL_TESTS();\n"])
        testFile.writelines(["}\n"])

        # Complete the doxygen group
        testFile.writelines(["\n"]) # whitespace for readability
        testFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def generateLangHFile(self, languageName, baseDirectory = "../output", subdir = "inc"):
        """!
        @brief Generate the language specific strings class include file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        string = subdir/name of the generated file
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateHFileName(languageName))
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeHFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus, retFileName

    def generateLangCppFile(self, languageName, baseDirectory = "../output", subdir = "src"):
        """!
        @brief Generate the language specific strings class cpp file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateCppFileName(languageName))
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeCppFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus, retFileName

    def generateLangUnittestFile(self, languageName, baseDirectory = "../output", subdir = "test"):
        """!
        @brief Generate the language specific strings class unittest file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateCppFileName(languageName))
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeUnittestFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus, retFileName

    def generateLangHFiles(self, baseDirectory = "../output", subdir = "inc"):
        """!
        @brief Generate all language specific strings class include files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated files
        """
        returnStatus = True
        fileList = []
        languageList = self.jsonLangData.getLanguageList()
        for languageName in languageList:
            fileStatus, filename = self.generateLangHFile(languageName, baseDirectory, subdir)
            fileList.append(filename)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus, fileList

    def generateLangCppFiles(self, baseDirectory = "../output", subdir = "src"):
        """!
        @brief Generate all language specific strings class cpp files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated files
        """
        returnStatus = True
        fileList = []
        languageList = self.jsonLangData.getLanguageList()
        for languageName in languageList:
            fileStatus, filename = self.generateLangCppFile(languageName, baseDirectory, subdir)
            fileList.append(filename)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus, fileList

    def generateLangUnittestFiles(self, baseDirectory = "../output", subdir = "test"):
        """!
        @brief Generate all language specific strings class unittest files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated files
        """
        returnStatus = True
        fileList = []
        languageList = self.jsonLangData.getLanguageList()
        for languageName in languageList:
            fileStatus, filename = self.generateLangUnittestFile(languageName, baseDirectory, subdir)
            fileList.append(filename)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus, fileList

    def generateLangFiles(self, baseDirectory = "../output", incSubdir = "inc", srcSubdir="src", testSubDir="test"):
        """!
        @brief Generate all language specific strings class files
        @param baseDirectory {string} Base File output directory
        @param incSubdir {string} Subdirectory to place include files in
        @param srcSubdir {string} Subdirectory to place cpp source files in
        @param testSubDir {string} Subdirectory to place unit test files in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated include files
                        list of strings = Sub-path/name of the generated source files
                        list of strings = Sub-path/name of the generated unittest source files
        """
        hfileStatus, hFileList = self.generateLangHFiles(baseDirectory, incSubdir)
        cppfileStatus, cppFileList = self.generateLangCppFiles(baseDirectory, srcSubdir)
        tstfileStatus, tstFileList = self.generateLangUnittestFiles(baseDirectory, testSubDir)
        finalStatus = hfileStatus and cppfileStatus and tstfileStatus
        return finalStatus, hFileList, cppFileList, tstFileList
