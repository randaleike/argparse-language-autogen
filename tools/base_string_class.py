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

from file_tools.static_lang_select import StaticLangSelectFunctionGenerator
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
        self.jsonLangData = LanguageDescriptionList(jsonLangFileName)
        self.jsonStringsData = StringClassDescription(jsonStringsFilename)

        self.osLangSelectList = [LinuxLangSelectFunctionGenerator(self.jsonLangData,
                                                                  dynamicCompileSwitch=StringClassNameGen.getDynamicCompileswitch()),
                                 WindowsLangSelectFunctionGenerator(self.jsonLangData,
                                                                    dynamicCompileSwitch=StringClassNameGen.getDynamicCompileswitch())
                                 # Add additional OS lang select classes here
                                 ]
        self.staticSelect = StaticLangSelectFunctionGenerator(self.jsonLangData,
                                                              dynamicCompileSwitch=StringClassNameGen.getDynamicCompileswitch())

        self.masterFunctionName = "getLocalParserStringListInterface"
        self.nameSpaceName = StringClassNameGen.getNamespaceName()
        self.masterFunction = MasterSelectFunctionGenerator(self.masterFunctionName,
                                                            StringClassNameGen.getBaseClassName(),
                                                            StringClassNameGen.getDynamicCompileswitch())

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
        cppFile.writelines(self.genIncludeBlock(includeFileList))

        # Add the parser string files
        languageList = self.jsonLangData.getLanguageList()
        for langName in languageList:
            langCompileSwitch = self.jsonLangData.getLanguageCompileSwitchData(langName)
            ifdef = "(defined("+langCompileSwitch+") || "+self.ifDynamicDefined+")\n"
            cppFile.writelines(["#if "+ifdef])
            cppFile.writelines(self._genInclude(self._generateHFileName(langName)))
            cppFile.writelines(["#endif // "+ifdef])

        # Add doxygen group start
        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(self._generateCppFileName(), self.groupName, self.groupDesc))

        cppFile.writelines(["\n"]) # whitespace for readability
        cppFile.writelines(self._genUsingNamespace(self.nameSpaceName))

        # Add the language dependent selection functions
        for langSelectFunction in self.osLangSelectList:
            cppFile.writelines(["\n"]) # whitespace for readability
            langSelectFunction.genFunction(cppFile)

        # Add the static selection function
        cppFile.writelines(["\n"]) # whitespace for readability
        self.staticSelect.genFunction(cppFile)

        # Add the master selection function
        cppFile.writelines(["\n"]) # whitespace for readability
        self.masterFunction.genFunction(cppFile, self.osLangSelectList, self.staticSelect)

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
            self._writeMethod(hFile, propertyMethod, propertyDesc, propertyParams, propertyReturn, prefix, postfix, False)
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
            self._writeMethod(hFile, translateMethodName, transDesc, transParams, transReturn, prefix, postfix, False)
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

        # Add the documented function declaration
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
        cppFile.writelines(self.doxyCommentGen.genDoxyDefgroup(langSelectObject.getUnittestFileName(),
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
        self.masterFunction.genUnitTest(getIsoName, cppFile, self.osLangSelectList, self.staticSelect)

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

    def generateCppFile(self, baseDirectory = "../output", subdir="src"):
        """!
        @brief Generate the base strings class selection implementation file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source file into
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = False
        retFileName = os.path.join(subdir, self._generateCppFileName())
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            cppFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeCppFile(cppFile)
            cppFile.close()
            returnStatus = True
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
        return returnStatus, retFileName

    def generateBaseHFile(self, baseDirectory = "../output", subdir="inc"):
        """!
        @brief Generate the base strings class include file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest include file into
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = False
        retFileName = os.path.join(subdir, self._generateHFileName())
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            hFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeBaseHFile(hFile)
            hFile.close()
            returnStatus = True
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
        return returnStatus, retFileName

    def generateUnittestFile(self, baseDirectory = "../output", subdir="test"):
        """!
        @brief Generate the base strings class unit test file
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source files into
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = True
        retFileName = os.path.join(subdir, self._generateUnittestFileName())
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            unittestFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeUnittestFile(unittestFile)
            unittestFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus, retFileName

    def generateOsSelectUnittestFile(self, langSelectObject, baseDirectory = "../output", subdir="test"):
        """!
        @brief Generate the base strings class unit test file
        @param langSelectObject {object} OS local language select object
        @param baseDirectory {string} Base File output directory
        @param subdir {string} Subdirectory to put the unittest source files into
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file
        """
        returnStatus = True
        retFileName = os.path.join(subdir, langSelectObject.getUnittestFileName())
        writeFileName = os.path.join(baseDirectory, retFileName)
        try:
            # open the file
            unittestFile = open(writeFileName, 'w', encoding='utf-8')
            self._writeSelectUnittestFile(langSelectObject, unittestFile)
            unittestFile.close()
        except:
            print("ERROR: Unable to open "+writeFileName+" for writing!")
            returnStatus = False

        return returnStatus, retFileName

    def generateOsSelectUnittestFiles(self, baseDirectory = "../output", testSubDir="test"):
        """!
        @brief Generate all OS local language select unit test files
        @param baseDirectory {string} Base File output directory
        @param testSubDir {string} Subdirectory to place unit test files in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated unit test cpp files
        """
        selectStatus = True
        selectUnittestFiles = []
        for langSelect in self.osLangSelectList:
            osSelectStatus, osSelectUnittestFile = self.generateOsSelectUnittestFile(langSelect, baseDirectory, testSubDir)
            if osSelectStatus:
                selectUnittestFiles.append(osSelectUnittestFile)
            else:
                selectStatus = False

        return selectStatus, selectUnittestFiles

    def generateStaticSelectUnittestFile(self, baseDirectory = "../output", testSubDir="test"):
        """!
        @brief Generate all OS local language select unit test files
        @param baseDirectory {string} Base File output directory
        @param testSubDir {string} Subdirectory to place unit test files in
        @return tuple - boolean = True for pass, else false for failure
                        list of strings = Sub-path/name of the generated unit test cpp files
        """
        return self.generateOsSelectUnittestFile(self.staticSelect, baseDirectory, testSubDir)

    def genBaseFiles(self, baseDirectory = "../output", incSubdir = "inc", srcSubdir="src", testSubDir="test"):
        """!
        @brief Generate all language specific strings class files
        @param baseDirectory {string} Base File output directory
        @param incSubdir {string} Subdirectory to place include files in
        @param srcSubdir {string} Subdirectory to place cpp source files in
        @param testSubDir {string} Subdirectory to place unit test files in
        @return tuple - boolean = True for pass, else false for failure
                        string = Sub-path/name of the generated file h file
                        string = Sub-path/name of the generated file cpp file
                        string = Sub-path/name of the generated file unit test cpp file
        """
        hstatus, hfile = self.generateBaseHFile(baseDirectory, incSubdir)
        cppstatus, cppFile = self.generateCppFile(baseDirectory, srcSubdir)
        unitStatus, unittestFile = self.generateUnittestFile(baseDirectory, testSubDir)

        selectStatus, selectUnittestFiles = self.generateOsSelectUnittestFiles(baseDirectory, testSubDir)
        staticSelectStatus, staticSelectFile = self.generateStaticSelectUnittestFile(baseDirectory, testSubDir)

        status = cppstatus and hstatus and unitStatus and selectStatus and staticSelectStatus
        return status, hfile, cppFile, unittestFile, selectUnittestFiles, staticSelectFile
