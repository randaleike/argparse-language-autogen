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

import argparse
import pathlib
import os

from pathgen import FileNameGenerator
from file_tools.common.eula import eula
from base_string_class import GenerateBaseLangFiles
from lang_string_class import GenerateLangFiles

def GenerateCmake(baseFileTuple, langFileListTuple, filePath):
    ## @todo implement this
    pass

def GenerateLanguageSelectFiles(jsonLangFileName, jsonStringsFilename, filePath, incfileSubdir, srcfileSubdir, tstfileSubdir, owner, eulaName):
    """!
    @brief Generate the string files

    @param jsonLangFileName {string} Path/Filename of the JSON language list file to use
    @param jsonStringsFilename {string} Path/Filename of the JSON property/translate string file to use
    @param filePath {string} path to the base directory
    @param incfileSubdir {string} path to put the include generated files
    @param srcfileSubdir {string} path to put the cpp source generated files
    @param tstfileSubdir {string} path to put the unit test generated files
    @param owner {string} Owner name to use in the copyright header message or None to use tool name
    @param eulaName {string} EULA text to use in the header message or None to default MIT Open
    """
    # Generate the base string files
    baseFileGen = GenerateBaseLangFiles(jsonLangFileName, jsonStringsFilename, owner, eulaName)
    cppStatus, cppFileName = baseFileGen.generateCppFile(filePath, srcfileSubdir)
    hStatus, hFileName = baseFileGen.generateBaseHFile(filePath, incfileSubdir)
    unittestStatus, unitTestFileName = baseFileGen.generateUnittestFile(filePath, tstfileSubdir)
    selectStatus, selectUnitTestFiles = baseFileGen.generateOsSelectUnittestFiles(filePath, tstfileSubdir)
    staticStatus, staticUnitTestFile = baseFileGen.generateStaticSelectUnittestFile(filePath, tstfileSubdir)

    langFileGen = GenerateLangFiles(jsonLangFileName, jsonStringsFilename, owner, eulaName)
    langHStatus, langHFileNames = langFileGen.generateLangHFiles(filePath, incfileSubdir)
    langCppStatus, langCppFileNames = langFileGen.generateLangCppFiles(filePath, srcfileSubdir)
    langtestStatus, langTestFileName = langFileGen.generateLangUnittestFiles(filePath, tstfileSubdir)

    if (hStatus and cppStatus and unittestStatus and
        langHStatus and langCppStatus and langtestStatus and
        selectStatus and staticStatus):
        GenerateCmake((hFileName, cppFileName, unitTestFileName, selectUnitTestFiles, staticUnitTestFile),
                      (langHFileNames, langCppFileNames, langTestFileName),
                      filePath)
    else:
        SystemExit(5)

def CommandMain():
    """!
    Utility command interface
    @param subcommand {string} JSON string file command
    """
    error = 0
    eulaNames = eula.keys()
    eulaHelp = "EULA name "
    first = True
    for name in eulaNames:
        if first:
            eulaHelp += '['
        else:
            eulaHelp += '|'
        eulaHelp += name
    eulaHelp+=']'

    parser = argparse.ArgumentParser(prog="autogenlang",
                                     description="Update argpaser library language string h/cpp/unittest files")
    parser.add_argument('-o','--outpath', dest='genfilepath', required=False, type=pathlib.Path,
                        default='../output', help='Existing destination directory')
    parser.add_argument('--owner', dest='owner', required=False, type=str, default=None, help='Owner name')
    parser.add_argument('--eula', dest='eula', required=False, type=str, default=None, help=eulaHelp)
    #parser.add_argument('subcommand', choices=['build'])
    args = parser.parse_args()

    # Build the output directories
    basefilePath = os.path.abspath(args.genfilepath)
    if not os.path.exists(basefilePath):
        os.makedirs(basefilePath)
    elif not os.path.isdir(basefilePath):
        print("Error: \""+basefilePath+"\" already exists as file.")
        SystemExit(1)

    srcfilePath = os.path.join(basefilePath, 'src')
    if not os.path.exists(srcfilePath):
        os.makedirs(srcfilePath)
    elif not os.path.isdir(srcfilePath):
        print("Error: \""+srcfilePath+"\" already exists as file.")
        SystemExit(2)

    incfilePath = os.path.join(basefilePath, 'inc')
    if not os.path.exists(incfilePath):
        os.makedirs(incfilePath)
    elif not os.path.isdir(incfilePath):
        print("Error: \""+incfilePath+"\" already exists as file.")
        SystemExit(3)

    unittestfilePath = os.path.join(basefilePath, 'test')
    if not os.path.exists(unittestfilePath):
        os.makedirs(unittestfilePath)
    elif not os.path.isdir(unittestfilePath):
        print("Error: \""+unittestfilePath+"\" already exists as file.")
        SystemExit(4)

    # Generate the files
    GenerateLanguageSelectFiles(FileNameGenerator.getLanguageDescriptionFileName("../data"),
                                FileNameGenerator.getStringClassDescriptionFileName("../data"),
                                basefilePath,
                                'inc',
                                'src',
                                'test',
                                args.owner,
                                args.eula)
    SystemExit(error)


if __name__ == '__main__':
    CommandMain()