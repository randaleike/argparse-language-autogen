"""@package autogenlang
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

from file_tools.json_data.jsonStringClassDescription import StringClassDescription

from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles

class CmakeGenerator(object):
    """!
    @brief Build cmake list file
    """
    def __init__(self, baseFileGen:GenerateBaseLangFiles, langFileGen:GenerateLangFiles,
                 incfileSubdir:list, mockIncdir:str, baseDir:str, jsonStringFile:StringClassDescription):
        """!
        @brief CmakeGenerator constructor
        @param baseFileGen {GenerateBaseLangFiles} Object used to generate the base interface files
        @param langFileGen {GenerateLangFiles} Object used to generate the language specific interface files
        @param incfileSubdir {list of strings} Include directory paths relative to the file base directory
        @param mockIncdir {string} Mock file output directory
        @param baseDir {string} Base directory name
        @param jsonStringFile {StringClassDescription} Class description file
        """
        self.baseFileGen = baseFileGen
        self.langFileGen = langFileGen
        self.versionMajor = 1
        self.versionMinor = 0
        self.versionPatch = 0
        self.versionTweak = 3
        self.incfileSubdir = incfileSubdir
        self.mockIncfileSubdir = [mockIncdir]
        self.baseDirName = baseDir
        self.dynamicSelectionSwitch = "-D"+jsonStringFile.getDynamicCompileSwitch()
        self.jsonStringFile = jsonStringFile

    def _generateUnittestBuild(self, desciption:str, sourceFiles:list, targetName:str,
                               includeDir:str, incCoverage:bool = True)->list:
        """!
        @brief Generate the language file unittest executable build

        @param desciption {string} Language name
        @param sourceFiles {list of string} CPP file names
        @param targetName {string} Target unit test executable name
        @param includeDir {string} Include directory list cmake macro name
        @param incCoverage {boolean} True = include unit test coverage code,
                                     False = Don't include unit test coverage code
        @param languageCompileSwitch {string | None} if None use dynamic compile switch,
                                                     else use the input language compile switch.

        @return list of strings - Build cmake code
        """
        buildCode=[]
        fileList=""
        for cppFile in sourceFiles:
            fileList+=" "
            fileList+=cppFile

        buildCode.append("####\n")
        buildCode.append("# "+desciption+" unit test build\n")
        buildCode.append("####\n")
        buildCode.append("add_executable("+targetName+" "+fileList+")\n")
        buildCode.append("target_include_directories("+targetName+" PUBLIC ${"+includeDir+"} ${GTEST_INCLUDE_DIR})\n")
        buildCode.append("target_link_libraries("+targetName+" PRIVATE ${GTEST_LIBRARIES})\n")
        buildCode.append("target_compile_options("+targetName+" PUBLIC -DGTEST_LINKED_AS_SHARED_LIBRARY=1)\n")

        if incCoverage:
            buildCode.append("if((${CMAKE_SYSTEM_NAME} MATCHES \"Linux\") AND (CMAKE_BUILD_TYPE MATCHES \"^[Dd]ebug\"))\n")
            buildCode.append("    target_compile_options("+targetName+" PRIVATE --coverage)\n")
            buildCode.append("    target_link_options("+targetName+" PRIVATE --coverage)\n")
            buildCode.append("endif()\n")
        buildCode.append("\n") #whitespace for readability

        testListName = targetName+"AllTests"
        buildCode.append("gtest_add_tests (TARGET "+targetName+" TEST_LIST "+testListName+")\n")
        buildCode.append("\n") #whitespace for readability

        buildCode.append("if(${CMAKE_SYSTEM_NAME} MATCHES \"Windows\")\n")
        buildCode.append("    set_tests_properties(${"+testListName+"} PROPERTIES ENVIRONMENT \"PATH=$<SHELL_PATH:$<TARGET_FILE_DIR:gtest>>$<SEMICOLON>$ENV{PATH}\")\n")
        buildCode.append("endif()\n")

        return buildCode

    def _generateLangUnittestBuild(self, languageName:str, cppFile:str, unittestFile:str,
                                   targetName:str, includeDir:str, incCoverage:bool = True)->list:
        """!
        @brief Generate the language file unittest executable build

        @param languageName {string} Language name
        @param cppFile {string} Language CPP file name
        @param unittestFile {string} Language unit test CPP filename
        @param targetName {string} Target unit test executable name
        @param includeDir {string} Include directory list cmake macro name
        @param incCoverage {boolean} True = include unit test coverage code,
                                     False = Don't include unit test coverage code

        @return list of strings - Build cmake code
        """
        sourceList = [cppFile, unittestFile]
        description = languageName+" string"
        return self._generateUnittestBuild(description, sourceList, targetName, includeDir, incCoverage)

    def generatecmakeIncFile(self, cmakeFile):
        """!
        @brief CMake include file if you need to link in the source files directly
        @param cmakeFile {file} Open file for output
        """
        # Build the library include path list
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# Language files include path\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set (languageStringsIncDir\n"])
        for dir in self.incfileSubdir:
            cmakeFile.writelines(["     ${MASTER_PROJECT_BASE_DIR}/"+self.baseDirName+"/"+dir+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        # Build the mock include path list
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# Language files mock include path\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set (languageStringsMockIncDir\n"])
        cmakeFile.writelines(["     ${languageStringsIncDir}\n"])
        for dir in self.mockIncfileSubdir:
            cmakeFile.writelines(["     ${MASTER_PROJECT_BASE_DIR}/"+self.baseDirName+"/"+dir+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        # Get the source file list
        libSrcFileList = [self.baseFileGen.getCmakeLibFileName()]
        libSrcFileList.extend(self.langFileGen.getCmakeLangLibFileNames())

        # Build Source List
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# Language source file list\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set (languageStringsSrc\n"])
        for fileNames in libSrcFileList:
            cmakeFile.writelines(["     ${MASTER_PROJECT_BASE_DIR}/"+self.baseDirName+"/"+fileNames+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        # Build Mock file List
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# Language mock file list\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set (languageStringsMockSrc\n"])
        cmakeFile.writelines(["     ${MASTER_PROJECT_BASE_DIR}/"+self.baseDirName+"/"+self.baseFileGen.getCmakeMockSrcFileName()+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

    def generateCmakeFile(self, cmakeFile):
        """!
        @brief Generate the CMakeLists.txt file
        @param cmakeFile {file} Open file for output
        """
        projectName = self.jsonStringFile.getBaseClassName()

        incFileList = [self.baseFileGen.getCmakeHFileName()]
        baseCppFile = self.baseFileGen.getCmakeLibFileName()
        libSrcFileList = [self.baseFileGen.getCmakeLibFileName()]

        incFileList.extend(self.langFileGen.getCmakeLangHFileNames())
        libSrcFileList.extend(self.langFileGen.getCmakeLangLibFileNames())

        # Define the project string
        projectStr = "project("
        projectStr += projectName
        projectStr +=" VERSION "
        projectStr += str(self.versionMajor)
        projectStr += "."
        projectStr += str(self.versionMinor)
        projectStr += "."
        projectStr += str(self.versionPatch)
        projectStr += "."
        projectStr += str(self.versionTweak)
        projectStr += " LANGUAGES C CXX DESCRIPTION \""
        projectStr += projectName
        projectStr += " Library\" HOMEPAGE_URL \""
        projectStr += "https://github.com/randaleike/argparse"
        projectStr += "\")\n"

        cmakeFile.writelines(["# "+projectName+" Library CMake file\n"])
        cmakeFile.writelines(["cmake_minimum_required(VERSION 3.14)\n"])
        cmakeFile.writelines([projectStr])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        cmakeFile.writelines(["set(CMAKE_CXX_STANDARD 17)\n"])
        cmakeFile.writelines(["set(CMAKE_CXX_STANDARD_REQUIRED True)\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        projectBaseInclude = projectName+"_baseInclude"
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# "+projectName+" Files\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set ("+projectBaseInclude+"\n"])
        for dir in self.incfileSubdir:
            cmakeFile.writelines(["     ${CMAKE_CURRENT_LIST_DIR}/"+dir+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        projectBaseSrc = projectName+"_baseSrc"
        cmakeFile.writelines(["set ("+projectBaseSrc+"\n"])
        for fileNames in libSrcFileList:
            cmakeFile.writelines(["     ${CMAKE_CURRENT_LIST_DIR}/"+fileNames+"\n"])
        cmakeFile.writelines(["     )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# "+projectName+" library\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["add_library(${PROJECT_NAME} OBJECT ${"+projectBaseSrc+"})\n"])
        cmakeFile.writelines(["target_include_directories(${PROJECT_NAME} PRIVATE ${"+projectBaseInclude+"})\n"])
        cmakeFile.writelines(["set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${PROJECT_VERSION})\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# "+projectName+" Unit tests\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["enable_testing()\n"])
        cmakeFile.writelines(["include(GoogleTest)\n"])
        cmakeFile.writelines(["\n"])

        # Output Language file unit test build
        languageUnitTestList = self.langFileGen.getCmakeCppUnitTestSets()
        for (languageName, cppFile, unittestFile, targetName) in languageUnitTestList:
            cmakeCode = self._generateLangUnittestBuild(languageName, cppFile, unittestFile, targetName, projectBaseInclude)
            cmakeFile.writelines(cmakeCode)
            cmakeFile.writelines(["\n"])

        # Output OS language select unit test build
        osSelectUnittests = self.baseFileGen.getCmakeSelectUnittestFileNames()
        for (selectUnittestFile, targetName) in osSelectUnittests:
            sourceList = ["${"+projectBaseSrc+"}", selectUnittestFile]
            cmakeCode = self._generateUnittestBuild("OS selection Unit test", sourceList, targetName, projectBaseInclude)
            cmakeFile.writelines(cmakeCode)
            cmakeFile.writelines(["\n"])

        # Output Base unittest
        projectBaseUnittest = projectName+"_baseUnittest"
        sourceList = ["${"+projectBaseSrc+"}", self.baseFileGen.getCmakeBaseUnittestFileName()]
        cmakeCode = self._generateUnittestBuild(projectBaseUnittest,
                                                sourceList,
                                                self.jsonStringFile.getBaseClassName()+"_test",
                                                projectBaseInclude)
        cmakeFile.writelines(cmakeCode)
        cmakeFile.writelines(["\n"])
