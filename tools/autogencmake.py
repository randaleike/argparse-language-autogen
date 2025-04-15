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

import pathlib
import os

from file_tools.string_class_tools import StringClassNameGen
from pathgen import FileNameGenerator
from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles

class CmakeGenerator(object):
    """!
    @brief Build cmake list file
    """
    def __init__(self, baseFileGen, langFileGen, incfileSubdir):
        """!
        @brief CmakeGenerator constructor
        """
        self.baseFileGen = baseFileGen
        self.langFileGen = langFileGen
        self.versionMajor = 0
        self.versionMinor = 5
        self.versionPatch = 0
        self.versionTweak = 0
        self.incfileSubdir = incfileSubdir

    def generateCmakeFile(self, cmakeFile):
        """!
        @brief Generate the CMakeLists.txt file
        @param cmakeFile {file} Open file for output
        """
        projectName = StringClassNameGen.getBaseClassName()

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
            cmakeFile.writelines(["    ${CMAKE_CURRENT_LIST_DIR}/"+dir+"\n"])
        cmakeFile.writelines(["    )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        projectBaseSrc = projectName+"_baseSrc"
        cmakeFile.writelines(["set ("+projectBaseSrc+"\n"])
        for fileName in self.libSrcFileList:
            cmakeFile.writelines(["    ${CMAKE_CURRENT_LIST_DIR}/"+fileName+"\n"])
        cmakeFile.writelines(["    )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# "+projectName+" library\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["add_library(${PROJECT_NAME} STATIC ${"+projectBaseSrc+"})\n"])
        cmakeFile.writelines(["target_include_directories(${PROJECT_NAME} PRIVATE ${"+projectBaseInclude+"})\n"])
        cmakeFile.writelines(["set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${PROJECT_VERSION})\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

        projectBaseUnittest = projectName+"_baseUnittest"
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["# "+projectName+" Unit test base\n"])
        cmakeFile.writelines(["####\n"])
        cmakeFile.writelines(["set ("+projectBaseSrc+"\n"])
        for fileName in self.libSrcFileList:
            cmakeFile.writelines(["    ${CMAKE_CURRENT_LIST_DIR}/"+fileName+"\n"])
        cmakeFile.writelines(["    )\n"])
        cmakeFile.writelines(["\n"]) # whitespace for readability

####
# parser_base Unit testing
####
set (parser_baseTest
    ${CMAKE_CURRENT_LIST_DIR}/test/parser_string_list_test.cpp
    ${CMAKE_CURRENT_LIST_DIR}/test/parser_base_test.cpp
    ${CMAKE_CURRENT_LIST_DIR}/test/parser_base_unittest.cpp
    )

set (parser_baseMockInc
    ${parser_baseInclude}
    ${MASTER_PROJECT_BASE_DIR}/varg/mock
    )

set (parser_baseTestMock
    )

set (parser_baseExternalLib
    varg
    )

enable_testing()

add_executable(${PROJECT_NAME}_test ${parser_baseSrc} ${parser_baseTestMock} ${parser_baseTest})
target_include_directories(${PROJECT_NAME}_test PUBLIC ${parser_baseInclude} ${parser_baseMockInc} ${GTEST_INCLUDE_DIR} ${GMOCK_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME}_test PRIVATE ${parser_baseExternalLib} ${GTEST_LIBRARIES})
target_compile_options(${PROJECT_NAME}_test PRIVATE -DGTEST_LINKED_AS_SHARED_LIBRARY=1)
if((${CMAKE_SYSTEM_NAME} MATCHES "Linux") AND (CMAKE_BUILD_TYPE MATCHES "^[Dd]ebug"))
    target_compile_options(${PROJECT_NAME}_test PRIVATE --coverage)
    target_link_options(${PROJECT_NAME}_test PRIVATE --coverage)
endif()

include(GoogleTest)
gtest_add_tests(TARGET ${PROJECT_NAME}_test TEST_LIST parserBaseAllTests)

if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set_tests_properties(${parserBaseAllTests} PROPERTIES ENVIRONMENT "PATH=$<SHELL_PATH:$<TARGET_FILE_DIR:gtest>>$<SEMICOLON>$ENV{PATH}")
endif()
