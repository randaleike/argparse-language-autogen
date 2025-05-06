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

from file_tools.json_data.jsonLanguageDescriptionList import LanguageDescriptionList
from file_tools.json_data.jsonStringClassDescription import StringClassDescription
from file_tools.json_data.jsonStringClassDescription import TranslationTextParser
from file_tools.json_data.param_return_tools import ParamRetDict

from file_tools.string_class_tools import BaseStringClassGenerator

class GenerateLangFiles(BaseStringClassGenerator):
    def __init__(self, languageList:LanguageDescriptionList, classStrings:StringClassDescription,
                 owner:str|None = None, eulaName:str|None = None):
        """!
        @brief GenerateLangFiles constructor

        @param languageList {StringClassDescription} JSON language list object
        @param classStrings {LanguageDescriptionList} JSON property/translate string object to use
        @param owner {string|None} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string|None} EULA text to use in the header message or None to default MIT Open
        """
        super().__init__(owner, eulaName, classStrings.getBaseClassName())
        self.versionMajor = 1
        self.versionMinor = 0
        self.versionPatch = 0
        self.versionTweak = 0

        self.jsonLangData = languageList
        self.jsonStringsData = classStrings
        self.nameSpaceName = classStrings.getNamespaceName()

        self.langFileNames = {}
        self.includeSubDir = []

        self.testParamValues = {'keyString': ("--myKey", True),
                                'envKeyString': ("MY_ENV_KEY", True),
                                'jsonKeyString': ("jsonkey:", True),
                                'xmlKeyString': ("<xmlkey>", True),
                                'nargs': ("3", False),
                                'nargsExpected': ("2", False),
                                'nargsFound': ("1", False),
                                'vargRange': ("<-100:100>", True),
                                'vargType': ("integer", True),
                                'valueString': ("23", True)
                                }

    def _addFile(self, languageName:str, fileType:str, fileName:str):
        if languageName in self.langFileNames:
            self.langFileNames[languageName][fileType] = fileName
        else:
            self.langFileNames[languageName] = {}
            self.langFileNames[languageName][fileType] = fileName


    def getCmakeLangHFileNames(self)->list:
        fileList = []
        for languageName, fileDict in self.langFileNames.items():
            fileList.append(fileDict['includeFile'])
        return fileList

    def getCmakeIncludeDirs(self)->list:
        return self.includeSubDir

    def getCmakeLangLibFileNames(self)->list:
        fileList = []
        for languageName, fileDict in self.langFileNames.items():
            fileList.append(fileDict['sourceFile'])
        return fileList

    def getCmakeCppUnitTestLangFiles(self, languageName:str)->tuple:
        if languageName in self.langFileNames:
            return self.langFileNames[languageName]['sourceFile'], self.langFileNames[languageName]['unittestFile']
        else:
            return None, None

    def getCmakeCppUnitTestSets(self)->list:
        """!
        @brief Get the language unit test requirements list
        @return list of tuples (string, string, string) - Language name,
                                                          CPP files name,
                                                          Unit test CPP file name,
                                                          Unit test target name
        """
        unittestSets = []
        languageList = self.jsonLangData.getLanguageList()
        for languageName in languageList:
            cppFile, unittestFile = self.getCmakeCppUnitTestLangFiles(languageName)
            cmakeTargetName = self._generateUnittestTargetName(languageName)
            unittestSets.append((languageName, cppFile, unittestFile, cmakeTargetName))

        return unittestSets

    def _getParamTestValue(self, paramName:str)->str:
        """!
        @brief Return the parameter test value
        @param paramName (string) Name fot the value
        @return string - Test value
        """
        if paramName in self.testParamValues:
            value, isText = self.testParamValues[paramName]
            if isText:
                return "\""+value+"\""
            else:
                return value
        else:
            return "42"

    def _genPropertyCode(self, langName:str, propertyName:str, propertyReturn:dict)->list:
        """!
        @brief Generate property function code
        @param langName {string} Language name
        @param propertyName {string} Language property name
        @param propertyReturn {dictionary} Property method return dictionary
        @return list of strings - Inline code
        """
        isText = LanguageDescriptionList.isLanguagePropertyText(propertyName)
        codeTxt = []

        if self._isReturnList(propertyReturn):
            # List case
            codeTxt.append(self._genFunctionRetType(propertyReturn)+"returnData;")
            dataList = self.jsonLangData.getLanguagePropertyData(langName, propertyName)

            # Determine data type
            for dataItem in dataList:
                codeTxt.append(self._genAddListStatment("returnData", dataItem, isText))
            codeTxt.append("return returnData;")
        else:
            # Single item case
            dataItem = self.jsonLangData.getLanguagePropertyData(langName, propertyName)
            codeTxt.append(self._genReturnStatment(dataItem, isText))

        return codeTxt

    def _writeIncPropertyMethods(self, hFile):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        """
        # Add the property fetch methods
        postfix = "final"

        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)

            # Output final declaration
            hFile.writelines(self._writeMethod(propertyMethod, propertyDesc, propertyParams, propertyReturn, None, postfix))

    def _writeSrcPropertyMethods(self, cppFile, langName:str, className:str):
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
            if len(propertyParams) == 0:
                postfix = "const"
            else:
                postfix = None

            # Output final declaration
            methodDef = self._defineFunctionWithDecorations(className+"::"+propertyMethod,
                                                           propertyDesc,
                                                           propertyParams,
                                                           propertyReturn,
                                                           False,
                                                           None,
                                                           postfix)
            cppFile.writelines(methodDef)

            # Get the language data replacements
            codeText = self._genPropertyCode(langName, propertyName, propertyReturn)

            # Output code body
            if len(codeText) == 1:
                cppFile.writelines(["{"+codeText[0]+"}\n"])
            else:
                bodyIndent = "".rjust(self.functionIndent, ' ')
                cppFile.writelines(["{\n"])
                for line in codeText:
                    cppFile.writelines([bodyIndent+line+"\n"])
                cppFile.writelines(["}\n"])

    def _writeIncTranslateMethods(self, hFile):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        """
        # Add the property fetch methods
        postfixFinal = "final"

        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)

            # Output the function
            hFile.writelines(self._writeMethod(translateMethodName, transDesc, transParams, transReturn, None, postfixFinal))

    def _genTranslateCode(self, streamDescList:list)->str:
        """!
        @brief Generate the string output code
        @param inlineStreamDescList {tuple list} Stream output tuple list
        @return string - Inline code
        """
        streamName = "parserstr"
        streamString = self._getParserStrStreamType()+" "+streamName+"; "
        streamString += streamName
        streamString += TranslationTextParser.assembleStream(streamDescList, "<<")
        streamString += "; return parserstr.str();"
        return streamString

    def _writeSrcTranslateMethods(self, cppFile, langName:str, className:str):
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
            if len(transParams) == 0:
                postfix = "const"
            else:
                postfix = None

            # Output final declaration
            methodDef = self._defineFunctionWithDecorations(className+"::"+translateMethodName,
                                                           transDesc,
                                                           transParams,
                                                           transReturn,
                                                           False,
                                                           None,
                                                           postfix,
                                                           None)
            cppFile.writelines(methodDef)

            # Get the language generation string if needed
            targetLang = self.jsonLangData.getLanguageIsoCodeData(langName)

            # Get the language data replacements
            streamDesc = self.jsonStringsData.getTranlateMethodTextData(translateMethodName, targetLang)
            codeText = self._genTranslateCode(streamDesc)

            # Output code body
            cppFile.writelines(["{"+codeText+"}\n"])

    def _writeHFile(self, hFile, langName:str):
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
                       self.jsonStringsData.getBaseClassName()+".h",]
        hFile.writelines(self._genIncludeBlock(includeList))
        hFile.writelines(["\n"]) # whitespace for readability
        hFile.writelines(["#pragma once\n"])

        # Set the class name
        className = self.jsonStringsData.getLanguageClassName(langName)
        hFile.writelines(["using namespace "+self.nameSpaceName+";\n"])

        # Start class definition
        hFile.writelines(self._genClassOpen(className,
                                            "Language specific parser error/help string generation interface",
                                            "public "+self.jsonStringsData.getBaseClassName(),
                                            "final"))
        hFile.writelines(["    public:\n"])

        # Add default Constructor/destructor definitions
        hFile.writelines(self._genClassDefaultConstructorDestructor(className, self.declareIndent, False, True))

        # Add the property fetch methods
        self._writeIncPropertyMethods(hFile)
        hFile.writelines(["\n"]) # whitespace for readability

        # Add the string generation methods
        self._writeIncTranslateMethods(hFile)

        # Close the class
        hFile.writelines(self._genClassClose(className))

    def _writeCppFile(self, cppFile, langName:str):
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
        cppFile.writelines(self._genIncludeBlock(includeFileList))

        className = self.jsonStringsData.getLanguageClassName(langName)
        cppFile.writelines(["using namespace "+self.nameSpaceName+";\n"])
        cppFile.writelines(["using "+self._getParserStrStreamType()+" = std::stringstream;\n", "\n"])

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

    def _generatePropertyUnittest(self, propertyMethod:str, langName:str)->list:
        """!
        @brief Generate the unit test for the input property method
        @param propertyMethod {string} Property function name
        @param langName {string} Language name
        @return list of strings - Test code to output
        """
        codeText = []
        propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)
        unitTestSectionName = self.jsonStringsData.getLanguageClassName(langName)
        bodyIndent = "".rjust(4, ' ')

        # Translate the return type
        codeText.append("TEST("+unitTestSectionName+", fetch"+propertyMethod+")\n")
        codeText.append("{\n")
        codeText.append(bodyIndent+self.jsonStringsData.getLanguageClassName(langName)+" testvar;\n")

        # Build the property function call
        fetchCode = self._genFunctionRetType(propertyReturn)
        fetchCode += "output = testvar."
        fetchCode += propertyMethod
        fetchCode += "("
        paramPrefix = ""
        for param in propertyParams:
            fetchCode += paramPrefix
            paramValue = self._getParamTestValue(ParamRetDict.getParamName(param))
            fetchCode += paramValue
            paramPrefix = ", "
        fetchCode += ");\n"
        codeText.append(bodyIndent+fetchCode)

        # Build the test assertion
        isList = ParamRetDict.isModList(ParamRetDict.getReturnTypeMod(propertyReturn))
        if LanguageDescriptionList.isLanguagePropertyText(propertyName):
            if isList:
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
            if isList:
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

    def _generateTranslateUnittest(self, translateMethodName:str, langName:str)->list:
        """!
        @brief Generate the unit test for the input property method
        @param propertyMethod {string} Property function name
        @param langName {string} Language name
        @return list of strings - Test code to output
        """
        codeText = []
        transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)
        unitTestSectionName = self.jsonStringsData.getLanguageClassName(langName)
        bodyIndent = "".rjust(4, ' ')

        # Translate the return type
        codeText.append("TEST("+unitTestSectionName+", print"+translateMethodName+")\n")
        codeText.append("{\n")
        codeText.append(bodyIndent+self.jsonStringsData.getLanguageClassName(langName)+" testvar;\n")

        # Build the property function call
        fetchCode = self._genFunctionRetType(transReturn)
        fetchCode += "output = testvar."
        fetchCode += translateMethodName
        fetchCode += "("
        paramPrefix = ""
        for param in transParams:
            paramType = ParamRetDict.getParamType(param)
            fetchCode += paramPrefix
            fetchCode += self._getParamTestValue(ParamRetDict.getParamName(param))
            paramPrefix = ", "
        fetchCode += ");\n"
        codeText.append(bodyIndent+fetchCode)

        # Build the expected string
        targetLang = self.jsonLangData.getLanguageIsoCodeData(langName)
        stringData = self.jsonStringsData.getTranlateMethodTextData(translateMethodName, targetLang)
        expectedString = TranslationTextParser.assembleTestReturnString(stringData, self.testParamValues)

        # Build the assertion test
        assertText = "EXPECT_STREQ(\""+expectedString+"\", output.c_str());\n"
        codeText.append(bodyIndent+assertText)
        codeText.append("}\n")
        return codeText

    def _writeUnittestFile(self, testFile, langName:str):
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
        testFile.writelines(self._genIncludeBlock(includeFileList))

        # Add doxygen group start
        testFile.writelines(["\n"]) # whitespace for readability
        testFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateUnittestFileName(),
                                                                self.groupName+langName+'unittest',
                                                                self.groupDesc+' '+langName+' unit test'))

        testFile.writelines(["\n"]) # whitespace for readability

        # Set the class name
        className = self.jsonStringsData.getLanguageClassName(langName)
        testFile.writelines(["using namespace "+self.nameSpaceName+";\n"])
        testFile.writelines(["using "+self._getParserStrStreamType()+" = std::stringstream;\n", "\n"])
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

    def generateLangHFile(self, languageName:str, baseDirectory:str = "../output", subdir:str = "inc")->bool:
        """!
        @brief Generate the language specific strings class include file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateHFileName(languageName))
        self._addFile(languageName, 'includeFile', retFileName)

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeHFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateLangCppFile(self, languageName:str, baseDirectory:str = "../output", subdir:str = "src")->bool:
        """!
        @brief Generate the language specific strings class cpp file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateCppFileName(languageName))
        self._addFile(languageName, 'sourceFile', retFileName)

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeCppFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateLangUnittestFile(self, languageName:str, baseDirectory:str = "../output", subdir:str = "test")->bool:
        """!
        @brief Generate the language specific strings class unittest file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateUnittestFileName(languageName))
        self._addFile(languageName, 'unittestFile', retFileName)

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeUnittestFile(hFile, languageName)
            hFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateLangHFiles(self, baseDirectory:str = "../output", subdir:str = "inc")->bool:
        """!
        @brief Generate all language specific strings class include files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        languageList = self.jsonLangData.getLanguageList()
        self.includeSubDir.append(subdir)

        for languageName in languageList:
            fileStatus = self.generateLangHFile(languageName, baseDirectory, subdir)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus

    def generateLangCppFiles(self, baseDirectory:str = "../output", subdir:str = "src")->bool:
        """!
        @brief Generate all language specific strings class cpp files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        languageList = self.jsonLangData.getLanguageList()

        for languageName in languageList:
            fileStatus = self.generateLangCppFile(languageName, baseDirectory, subdir)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus

    def generateLangUnittestFiles(self, baseDirectory:str = "../output", subdir:str = "test")->bool:
        """!
        @brief Generate all language specific strings class unittest files
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to place file in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        languageList = self.jsonLangData.getLanguageList()

        for languageName in languageList:
            fileStatus = self.generateLangUnittestFile(languageName, baseDirectory, subdir)

            if not fileStatus:
                returnStatus = False
                break

        return returnStatus

    def generateLangFiles(self, baseDirectory:str = "../output", incSubdir:str = "inc",
                          srcSubdir:str = "src", testSubDir:str = "test")->bool:
        """!
        @brief Generate all language specific strings class files
        @param baseDirectory {string} Base File output directory
        @param incSubdir {string} Subdirectory to place include files in
        @param srcSubdir {string} Subdirectory to place cpp source files in
        @param testSubDir {string} Subdirectory to place unit test files in
        @return boolean = True for pass, else false for failure
        """
        hfileStatus = self.generateLangHFiles(baseDirectory, incSubdir)
        cppfileStatus = self.generateLangCppFiles(baseDirectory, srcSubdir)
        tstfileStatus = self.generateLangUnittestFiles(baseDirectory, testSubDir)
        finalStatus = hfileStatus and cppfileStatus and tstfileStatus
        return finalStatus
