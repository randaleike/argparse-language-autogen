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
from file_tools.string_name_generator import StringClassNameGen

from file_tools.string_class_tools import BaseStringClassGenerator

from file_tools.linux_lang_select import LinuxLangSelectFunctionGenerator
from file_tools.windows_lang_select import WindowsLangSelectFunctionGenerator
# Add additional OS lang select classes here

from file_tools.master_lang_select import MasterSelectFunctionGenerator


class GenerateBaseLangFiles(BaseStringClassGenerator):
    def __init__(self, jsonLangFileName, jsonStringsFilename, owner = None, eulaName = None):
        """!
        @brief GenerateBaseLangFile constructor

        @param jsonLangFileName {string} Path/Filename of the JSON language list file to use
        @param jsonStringsFilename {string} Path/Filename of the JSON property/translate string file to use
        @param owner {string} Owner name to use in the copyright header message or None to use tool name
        @param eulaName {string} EULA text to use in the header message or None to default MIT Open
        """
        super().__init__(owner, eulaName)
        self.versionMajor = 1
        self.versionMinor = 0
        self.versionPatch = 0
        self.versionTweak = 0

        self.jsonLangData = LanguageDescriptionList(jsonLangFileName)
        self.jsonStringsData = StringClassDescription(jsonStringsFilename)

        self.osLangSelectList = [LinuxLangSelectFunctionGenerator(self.jsonLangData,
                                                                  dynamicCompileSwitch=StringClassNameGen.getDynamicCompileswitch()),
                                 WindowsLangSelectFunctionGenerator(self.jsonLangData,
                                                                    dynamicCompileSwitch=StringClassNameGen.getDynamicCompileswitch())
                                 # Add additional OS lang select classes here
                                 ]

        self.masterFunctionName = "getLocalParserStringListInterface"
        self.nameSpaceName = StringClassNameGen.getNamespaceName()
        self.masterFunction = MasterSelectFunctionGenerator(self.masterFunctionName,
                                                            StringClassNameGen.getBaseClassName(),
                                                            StringClassNameGen.getDynamicCompileswitch())

        self.hFileName = self._generateHFileName()
        self.mockHFileName = self._generateMockHFileName()
        self.cppFileName = self._generateCppFileName()
        self.unittestBaseFile = self._generateUnittestFileName()
        self.unittestSelectFiles = []
        self.includeSubDir = []
        self.staticUnittestFile = ""

    def getCmakeHFileName(self):
        return self.hFileName

    def getCmakeIncludeDirs(self):
        return self.includeSubDir

    def getCmakeLibFileName(self):
        return self.cppFileName

    def getCmakeBaseUnittestFileName(self):
        return self.unittestBaseFile

    def getCmakeSelectUnittestFileNames(self):
        return self.unittestSelectFiles

    def getCmakeMockFileName(self):
        return self.mockHFileName

    def _writeCppFile(self, cppFile):
        """!
        @brief Write the OS language selection CPP file
        @param cppFile {File} File to write the data to
        """
        # Write the common header data
        cppFile.writelines(self._generateFileHeader())
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the common includes
        includeFileList = ["<memory>", "<cstring>", "<string>", self._generateHFileName()]
        languageList = self.jsonLangData.getLanguageList()
        for langName in languageList:
            includeFileList.append(self._generateHFileName(langName))
        cppFile.writelines(self.genIncludeBlock(includeFileList))

        # Add doxygen group start
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateCppFileName(), self.groupName, self.groupDesc))

        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self._genUsingNamespace(self.nameSpaceName))

        # Add the language dependent selection functions
        for langSelectFunction in self.osLangSelectList:
            cppFile.writelines(["\n"]) # whitespace for readability
            langSelectFunction.genFunction(cppFile)

        # Add the master selection function
        cppFile.writelines(["\n"]) # whitespace for readability
        self.masterFunction.genFunction(cppFile, self.osLangSelectList)

        # Complete the doxygen group
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def _writePropertyMethods(self, hFile):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        """
        # Add the property fetch methods
        postfix = "= 0"
        prefix = '[[nodiscard]] virtual'

        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)
            hFile.writelines(self._writeMethod(propertyMethod, propertyDesc, propertyParams, propertyReturn, prefix, postfix, False))
            hFile.writelines(["\n"]) # whitespace for readability

    def _writeTranslateMethods(self, hFile):
        """!
        @brief Write the property method definitions

        @param hFile {File} File to write the data to
        @param langName {string} Language name or None this is for the base file
        """
        # Add the tranlate strings methods
        postfix = "= 0"
        prefix = '[[nodiscard]] virtual'

        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)
            hFile.writelines(self._writeMethod(translateMethodName, transDesc, transParams, transReturn, prefix, postfix, False))
            hFile.writelines(["\n"]) # whitespace for readability

    def _writeBaseHFile(self, hFile):
        """!
        @brief Write the OS language selection CPP file
        @param hFile {File} File to write the data to
        """
        # Write the common header datajsonStringsDef
        hFile.writelines(self._generateFileHeader())
        hFile.writelines(["\n"]) # whitespace for readability

        includeList = ["<cstddef>", "<cstdlib>", "<memory>", "<string>"]
        hFile.writelines(self.genIncludeBlock(includeList))

        hFile.writelines(["\n"]) # whitespace for readability
        hFile.writelines(self.doxyCommentGen.genDoxyDefgroup(StringClassNameGen.getBaseClassName()+".h", self.groupName, self.groupDesc))
        hFile.writelines(["#pragma once\n"])

        hFile.writelines(["\n",
                        "using "+StringClassNameGen.getParserStringType()+" = std::string;          ///< Standard parser string definition\n",
                        "using "+StringClassNameGen.getParserCharType()+" = char;                ///< Standard parser character definition\n",
                        "\n"]),
        hFile.writelines(self.genNamespaceOpen(self.nameSpaceName))
        hFile.writelines(["\n"]) # whitespace for readability

        # Start class definition
        className = StringClassNameGen.getBaseClassName()
        hFile.writelines(self.genClassOpen(className,
                                           "Parser error/help string generation interface"))
        hFile.writelines(["    public:\n"])

        # Add default Constructor/destructor definitions
        hFile.writelines(self.genClassDefaultConstructorDestructor(className,
                                                                   self.declareIndent,
                                                                   True,
                                                                   False))

        # Generate the property fetch methods
        self._writePropertyMethods(hFile)

        # Generate the translated string generation methods
        self._writeTranslateMethods(hFile)

        # Add the static generation function declaration
        methodName, briefDesc, retDict, paramList = self.masterFunction.getFunctionDesc()
        declText = self.declareFunctionWithDecorations(methodName,
                                                briefDesc,
                                                paramList,
                                                retDict,
                                                self.declareIndent,
                                                False,
                                                "static")
        hFile.writelines(declText)

        # Close the class and namespace
        hFile.writelines(self.genClassClose(className))
        hFile.writelines(["\n"]) # whitespace for readability
        hFile.writelines(self.genNamespaceClose(self.nameSpaceName))

        # Complete the doxygen group
        hFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def _writeSelectUnittestFile(self, langSelectObject, cppFile):
        """!
        @brief Write the OS language selection CPP file
        @param langSelectObject {object} OS local language select object
        @param cppFile {File} File to write the data to
        """
        getIsoName = self.jsonStringsData.getIsoPropertyMethodName()

        # Write the common header data
        cppFile.writelines(self._generateFileHeader())
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the common includes
        includeFileList = ["<gtest/gtest.h>", self._generateHFileName()]
        cppFile.writelines(self.genIncludeBlock(includeFileList))

        # Add doxygen group start
        cppFile.writelines(["\n"]) # whitespace for readability
        fileName, targetName = langSelectObject.getUnittestFileName()
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(fileName,
                                                               self.groupName+'unittest',
                                                               self.groupDesc+'unit test'))

        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self._genUsingNamespace(self.nameSpaceName))

        # Add the language dependent selection functions
        langSelectObject.genUnitTest(getIsoName, cppFile)

        # Add the test main
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(["// Execute the tests\n"])
        cppFile.writelines(["int main(int argc, char **argv)\n"])
        cppFile.writelines(["{\n"])
        cppFile.writelines(["    ::testing::InitGoogleTest(&argc, argv);\n"])
        cppFile.writelines(["    return RUN_ALL_TESTS();\n"])
        cppFile.writelines(["}\n"])

        # Complete the doxygen group
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def _writeUnittestFile(self, cppFile):
        """!
        @brief Write the OS language selection CPP file
        @param cppFile {File} File to write the data to
        """
        getIsoName = self.jsonStringsData.getIsoPropertyMethodName()

        # Write the common header data
        cppFile.writelines(self._generateFileHeader())
        cppFile.writelines(["\n"]) # whitespace for readability

        # Add the common includes
        includeFileList = ["<gtest/gtest.h>", self._generateHFileName()]
        cppFile.writelines(self.genIncludeBlock(includeFileList))

        # Add doxygen group start
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateUnittestFileName(),
                                                               self.groupName+'unittest',
                                                               self.groupDesc+'unit test'))

        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self._genUsingNamespace(self.nameSpaceName))

        # Add the master selection function
        cppFile.writelines(["\n"]) # whitespace for readability
        self.masterFunction.genUnitTest(getIsoName, cppFile, self.osLangSelectList)

        # Add the test main
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(["// Execute the tests\n"])
        cppFile.writelines(["int main(int argc, char **argv)\n"])
        cppFile.writelines(["{\n"])
        cppFile.writelines(["    ::testing::InitGoogleTest(&argc, argv);\n"])
        cppFile.writelines(["    return RUN_ALL_TESTS();\n"])
        cppFile.writelines(["}\n"])

        # Complete the doxygen group
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def _writeMockFile(self, mockFile):
        """!
        @brief Write the OS language selection CPP file
        @param hFile {File} File to write the data to
        """
        # Write the common header datajsonStringsDef
        mockFile.writelines(self._generateFileHeader())
        mockFile.writelines(["\n"]) # whitespace for readability

        includeList = ["<cstddef>",
                       "<cstdlib>",
                       "<memory>",
                       "<string>",
                       "<gmock/gmock.h>",
                       self._generateHFileName()
                       ]
        mockFile.writelines(self.genIncludeBlock(includeList))
        mockFile.writelines(["\n"]) # whitespace for readability

        mockFile.writelines(self.doxyCommentGen.genDoxyDefgroup(StringClassNameGen.getBaseClassName()+".h", self.groupName, self.groupDesc))
        mockFile.writelines(["\n"]) # whitespace for readability
        mockFile.writelines(["#pragma once\n"])

        mockFile.writelines(self.genNamespaceOpen(self.nameSpaceName))
        mockFile.writelines(["\n"]) # whitespace for readability

        # Start class definition
        className = StringClassNameGen.getBaseClassName()
        mockFile.writelines(self.genClassOpen("mock_"+className,
                                              "Mock Parser error/help string generation interface",
                                              "public "+className,
                                              "final"))
        mockFile.writelines(["    public:\n"])

        # Add default Constructor/destructor definitions
        mockFile.writelines(self.genClassDefaultConstructorDestructor(className,
                                                                      self.declareIndent,
                                                                      True,
                                                                      True,
                                                                      True))

        # Generate the property fetch methods
        postfix = "final"
        propertyMethodList = self.jsonStringsData.getPropertyMethodList()
        for propertyMethod in propertyMethodList:
            propertyName, propertyDesc, propertyParams, propertyReturn = self.jsonStringsData.getPropertyMethodData(propertyMethod)
            mockFile.writelines(self._writeMockMethod(propertyMethod, propertyParams, propertyReturn, postfix))

        # Generate the translated string generation methods
        tranlateMethodList = self.jsonStringsData.getTranlateMethodList()
        for translateMethodName in tranlateMethodList:
            transDesc, transParams, transReturn = self.jsonStringsData.getTranlateMethodFunctionData(translateMethodName)
            mockFile.writelines(self._writeMockMethod(translateMethodName, transParams, transReturn, postfix))

        # Close the class and namespace
        mockFile.writelines(self.genClassClose(className))
        mockFile.writelines(["\n"]) # whitespace for readability

        # Add the OS local language fetch override
        selectMethodName, selectBriefDesc, selectRetDict, selectParamList = self.masterFunction.getFunctionDesc()

        functionDef = self.defineFunctionWithDecorations(self.baseClassName+"::"+selectMethodName,
                                                         selectBriefDesc,
                                                         selectParamList,
                                                         selectRetDict,
                                                         True)

        functionDef.append("{return std::make_shared<mock_"+className+">();}\n")
        functionDef.append("\n")  # whitespace for readability

        mockFile.writelines(functionDef)
        mockFile.writelines(self.genNamespaceClose(self.nameSpaceName))

        # Complete the doxygen group
        mockFile.writelines(self.doxyCommentGen.genDoxyGroupEnd())

    def generateCppFile(self, baseDirectory = "../output", subdir="src"):
        """!
        @brief Generate the base strings class selection implementation file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source file into
        @return boolean - True for pass, else false for failure
        """
        returnStatus = False
        retFileName = os.path.join(subdir, self._generateCppFileName())
        self.cppFileName = retFileName

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            cppFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeCppFile(cppFile)
            cppFile.close()
            returnStatus = True
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")

        return returnStatus

    def generateBaseHFile(self, baseDirectory = "../output", subdir="inc"):
        """!
        @brief Generate the base strings class include file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest include file into
        @return boolean - True for pass, else false for failure
        """
        returnStatus = False
        retFileName = os.path.join(subdir, self._generateHFileName())
        self.includeSubDir.append(subdir)
        self.hFileName = retFileName

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeBaseHFile(hFile)
            hFile.close()
            returnStatus = True
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")

        return returnStatus

    def generateUnittestFile(self, baseDirectory = "../output", subdir="test"):
        """!
        @brief Generate the base strings class unit test file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source files into
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateUnittestFileName())
        self.unittestBaseFile = retFileName

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            unittestFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeUnittestFile(unittestFile)
            unittestFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateOsSelectUnittestFile(self, langSelectObject, baseDirectory = "../output", subdir="test"):
        """!
        @brief Generate the base strings class unit test file
        @param langSelectObject {object} OS local language select object
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source files into
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        fileName, targetName = langSelectObject.getUnittestFileName()
        retFileName = os.path.join(subdir, fileName)
        self.unittestSelectFiles.append((retFileName, targetName))

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            unittestFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeSelectUnittestFile(langSelectObject, unittestFile)
            unittestFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateOsSelectUnittestFiles(self, baseDirectory = "../output", testSubDir="test"):
        """!
        @brief Generate all OS local language select unit test files
        @param baseDirectory {string} Base File output directory
        @param testSubDir {string} Subdirectory to place unit test files in
        @return boolean - True for pass, else false for failure
        """
        selectStatus = True
        for langSelect in self.osLangSelectList:
            osSelectStatus = self.generateOsSelectUnittestFile(langSelect, baseDirectory, testSubDir)
            if not osSelectStatus:
                selectStatus = False

        return selectStatus

    def generateStaticSelectUnittestFile(self, baseDirectory = "../output", testSubDir="test"):
        """!
        @brief Generate all OS local language select unit test files
        @param baseDirectory {string} Base File output directory
        @param testSubDir {string} Subdirectory to place unit test files in
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        fileName, targetName = self.staticSelect.getUnittestFileName()

        retFileName = os.path.join(testSubDir, fileName)
        self.staticUnittestFile = retFileName

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            unittestFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeSelectUnittestFile(self.staticSelect, unittestFile)
            unittestFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def generateMockFile(self, baseDirectory = "../output", subdir="mock"):
        """!
        @brief Generate the base strings class unit test file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the mock files into
        @return boolean - True for pass, else false for failure
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateMockHFileName())
        self.mockHFileName = retFileName

        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            mockFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeMockFile(mockFile)
            mockFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus

    def genBaseFiles(self, baseDirectory = "../output", incSubdir = "inc", srcSubdir="src", testSubDir="test", mockSubDir = "mock"):
        """!
        @brief Generate all language specific strings class files

        @param baseDirectory {string} Base File output directory
        @param incSubdir {string} Subdirectory to place include files in
        @param srcSubdir {string} Subdirectory to place cpp source files in
        @param testSubDir {string} Subdirectory to place unit test files in
        @param mockSubDir {string} Subdirectory to place mock files  for external unit tests in

        @return boolean = True for pass, else false for failure
        """
        hstatus = self.generateBaseHFile(baseDirectory, incSubdir)
        cppstatus = self.generateCppFile(baseDirectory, srcSubdir)
        unitStatus = self.generateUnittestFile(baseDirectory, testSubDir)
        mockStatus = self.generateMockFile(baseDirectory, mockSubDir)

        selectStatus = self.generateOsSelectUnittestFiles(baseDirectory, testSubDir)
        #staticSelectStatus = self.generateStaticSelectUnittestFile(baseDirectory, testSubDir)

        status = cppstatus and hstatus and unitStatus and selectStatus and mockStatus
        return status
